"""
강화된 대화 서비스 - 메모리를 실제로 활용하는 채팅 시스템
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import ollama
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.memory_manager_simple import SimpleMemoryManager
from core.classification_service import ClassificationService
from config.settings import load_config, AppConfig

logger = logging.getLogger(__name__)


class EnhancedChatService:
    """메모리를 실제로 활용하는 대화 서비스"""

    def __init__(self, config: Optional[AppConfig] = None):
        """초기화"""
        self.config = config or load_config()
        self.memory_manager = SimpleMemoryManager(config)
        self.classifier = ClassificationService(config)
        self.sessions = {}

    async def chat(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        use_memory: bool = True
    ) -> Dict[str, Any]:
        """메모리 기반 대화 처리"""
        try:
            # 세션 초기화
            if session_id and session_id not in self.sessions:
                self.sessions[session_id] = []

            # 1. 관련 메모리 검색
            relevant_memories = []
            memory_context = ""

            if use_memory:
                logger.info(f"메모리 검색 중: {message}")
                relevant_memories = await self.memory_manager.search_memories(
                    query=message,
                    user_id=user_id,
                    limit=5
                )

                # 모든 메모리도 가져오기 (최근 10개)
                all_memories = await self.memory_manager.get_all_memories(
                    user_id=user_id,
                    limit=10
                )

                # 메모리 컨텍스트 구성
                memory_context = self._build_memory_context(
                    relevant_memories,
                    all_memories,
                    user_id
                )

                logger.info(f"메모리 컨텍스트: {memory_context[:200]}...")

            # 2. LLM에 메모리 컨텍스트와 함께 전달
            response_text = await self._generate_response_with_memory(
                message=message,
                memory_context=memory_context,
                session_history=self.sessions.get(session_id, [])
            )

            # 3. 대화에서 중요 정보 추출 및 저장
            await self._extract_and_save_info(
                user_message=message,
                ai_response=response_text,
                user_id=user_id
            )

            # 4. 세션 히스토리 업데이트
            if session_id:
                self.sessions[session_id].append({
                    "role": "user",
                    "content": message
                })
                self.sessions[session_id].append({
                    "role": "assistant",
                    "content": response_text
                })
                # 최근 20개만 유지
                if len(self.sessions[session_id]) > 20:
                    self.sessions[session_id] = self.sessions[session_id][-20:]

            # 5. 응답 구성
            response = {
                "response": response_text,
                "user_message": message,
                "used_memories": [
                    {
                        "id": mem.get("id"),
                        "text": mem.get("text", ""),
                        "score": mem.get("score", 0)
                    }
                    for mem in relevant_memories[:3]
                ],
                "memory_context": memory_context[:500] if memory_context else "",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

            return response

        except Exception as e:
            logger.error(f"대화 처리 실패: {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": "죄송합니다. 일시적인 오류가 발생했습니다.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _build_memory_context(
        self,
        relevant_memories: List[Dict],
        all_memories: List[Dict],
        user_id: str
    ) -> str:
        """메모리를 기반으로 풍부한 컨텍스트 구성"""
        context_parts = []

        # 사용자 기본 정보 추출
        user_info = {}
        preferences = []
        experiences = []

        # 모든 메모리에서 정보 추출
        for memory in all_memories:
            text = memory.get("text", "").lower()
            metadata = memory.get("metadata", {})
            category = metadata.get("category", "")

            # 개인정보 추출
            if "이름" in text or "name" in text:
                user_info["name"] = memory.get("text", "")
            elif "나이" in text or "age" in text or "살" in text:
                user_info["age"] = memory.get("text", "")
            elif "직업" in text or "job" in text or "일" in text:
                user_info["job"] = memory.get("text", "")

            # 선호도 추출
            if "좋아" in text or "싫어" in text or "prefer" in text:
                preferences.append(memory.get("text", ""))

            # 경험 추출
            if category == "experiences" or "경험" in text or "했" in text:
                experiences.append(memory.get("text", ""))

        # 컨텍스트 구성
        if user_info:
            context_parts.append("=== 사용자 정보 ===")
            for key, value in user_info.items():
                context_parts.append(f"- {value}")

        if preferences:
            context_parts.append("\n=== 선호도 ===")
            for pref in preferences[:3]:  # 최대 3개
                context_parts.append(f"- {pref}")

        if experiences:
            context_parts.append("\n=== 과거 경험 ===")
            for exp in experiences[:2]:  # 최대 2개
                context_parts.append(f"- {exp}")

        # 관련 메모리 추가
        if relevant_memories:
            context_parts.append("\n=== 현재 대화와 관련된 정보 ===")
            for memory in relevant_memories[:3]:
                context_parts.append(f"- {memory.get('text', '')}")

        if not context_parts:
            return ""

        full_context = "\n".join(context_parts)
        return full_context

    async def _generate_response_with_memory(
        self,
        message: str,
        memory_context: str,
        session_history: List[Dict]
    ) -> str:
        """메모리 컨텍스트를 포함하여 응답 생성"""
        try:
            messages = []

            # 시스템 프롬프트 - 메모리 활용 강조
            system_prompt = """당신은 사용자를 기억하는 AI 어시스턴트입니다.
제공된 사용자 정보와 과거 기억을 바탕으로 개인화된 대화를 진행하세요.

중요 지침:
1. 사용자에 대해 알고 있는 정보를 자연스럽게 대화에 활용하세요
2. 이전에 나눈 대화나 정보를 기억하고 있음을 보여주세요
3. 사용자의 선호도를 고려하여 답변하세요
4. 모순된 정보가 있다면 최신 정보를 우선시하세요
5. 한국어로 친근하게 대화하세요"""

            messages.append({
                "role": "system",
                "content": system_prompt
            })

            # 메모리 컨텍스트가 있으면 추가
            if memory_context:
                context_message = f"""다음은 사용자에 대해 기억하고 있는 정보입니다:

{memory_context}

위 정보를 참고하여 대화하되, 너무 인위적으로 언급하지 마세요.
자연스럽게 대화 흐름에 맞춰 활용하세요."""

                messages.append({
                    "role": "system",
                    "content": context_message
                })

            # 최근 대화 히스토리 추가 (최대 6개)
            for msg in session_history[-6:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # 현재 메시지 추가
            messages.append({
                "role": "user",
                "content": message
            })

            # Ollama 호출
            logger.info(f"Ollama 호출 - 모델: {self.config.models.chat_model}")
            response = ollama.chat(
                model=self.config.models.chat_model,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512
                }
            )

            return response['message']['content']

        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            return "죄송합니다. 응답을 생성하는 중 문제가 발생했습니다."

    async def _extract_and_save_info(
        self,
        user_message: str,
        ai_response: str,
        user_id: str
    ):
        """대화에서 중요 정보 추출 및 저장"""
        try:
            logger.debug(f"정보 추출 시작 - 사용자: {user_id}")
            logger.debug(f"메시지: {user_message[:100]}...")

            # 사용자 메시지에서 중요 정보 추출 (더 넓은 범위)
            important_keywords = [
                "이름", "나이", "살", "직업", "일", "회사",
                "좋아", "싫어", "관심", "취미", "즐겨", "선호",
                "사는", "거주", "출신", "살아", "집",
                "공부", "전공", "학교", "대학", "졸업",
                "가족", "부모", "형제", "자매", "친구",
                "음식", "먹", "마시", "요리",
                "여행", "가", "갔", "갈", "방문",
                "운동", "스포츠", "건강",
                "영화", "책", "음악", "게임",
                "습니다", "입니다", "에요", "이에요", "예요"
            ]

            # 키워드가 포함된 경우 메모리 저장
            should_save = any(keyword in user_message for keyword in important_keywords)
            logger.debug(f"키워드 매칭: {should_save}")

            # 명시적인 개인정보 패턴 확인 (더 넓은 패턴)
            personal_patterns = [
                "저는", "제가", "나는", "내가",
                "제 이름", "내 이름",
                "저의", "나의", "제", "내",
                "전 ", "난 ", "저 ",
                "있습니다", "있어요", "합니다", "해요"
            ]

            if any(pattern in user_message for pattern in personal_patterns):
                should_save = True
                logger.debug(f"개인정보 패턴 감지")

            # 메시지 길이 체크 (너무 짧은 메시지는 제외)
            if len(user_message) < 5:
                should_save = False
                logger.debug(f"메시지 너무 짧음: {len(user_message)} 글자")

            if should_save:
                # 분류
                category = await self.classifier.classify_text(user_message)
                logger.info(f"메모리 저장 시도 - 카테고리: {category}")

                # 메모리 저장
                memory_id = await self.memory_manager.add_memory(
                    text=user_message,
                    user_id=user_id,
                    metadata={
                        "source": "conversation",
                        "category": category,
                        "auto_extracted": True
                    }
                )
                logger.info(f"✅ 메모리 자동 저장 완료: ID={memory_id}, 내용={user_message[:50]}...")

                # 저장 확인
                all_memories = await self.memory_manager.get_all_memories(user_id)
                logger.info(f"현재 총 메모리 수: {len(all_memories)}개")
            else:
                logger.debug(f"저장할 정보 없음: {user_message[:50]}...")

        except Exception as e:
            logger.error(f"❌ 정보 추출 실패: {e}")
            import traceback
            traceback.print_exc()

    def clear_session(self, session_id: str):
        """세션 초기화"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"세션 삭제: {session_id}")

    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """세션 히스토리 반환"""
        return self.sessions.get(session_id, [])