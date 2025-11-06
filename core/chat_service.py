"""
대화 서비스 - Ollama와 mem0를 연동한 채팅 시스템
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import ollama
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.memory_manager_simple import SimpleMemoryManager
from core.classification_service import ClassificationService
from config.settings import load_config, AppConfig

logger = logging.getLogger(__name__)


class ChatService:
    """메모리 기반 대화 서비스"""

    def __init__(self, config: Optional[AppConfig] = None):
        """
        채팅 서비스 초기화

        Args:
            config: 애플리케이션 설정
        """
        self.config = config or load_config()
        self.memory_manager = SimpleMemoryManager(config)
        self.classifier = ClassificationService(config)

        # 대화 히스토리 (세션별)
        self.sessions = {}

    async def chat(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        use_memory: bool = True
    ) -> Dict[str, Any]:
        """
        메모리 기반 대화 처리

        Args:
            message: 사용자 메시지
            user_id: 사용자 ID
            session_id: 세션 ID
            use_memory: 메모리 사용 여부

        Returns:
            Dict: 응답 및 관련 정보
        """
        try:
            # 세션 초기화
            if session_id and session_id not in self.sessions:
                self.sessions[session_id] = []

            # 1. 관련 메모리 검색
            relevant_memories = []
            if use_memory:
                relevant_memories = await self.memory_manager.search_memories(
                    query=message,
                    user_id=user_id,
                    limit=5,
                    threshold=self.config.memory.similarity_threshold
                )

            # 2. 컨텍스트 구성
            context = self._build_context(relevant_memories, user_id)

            # 3. 대화 히스토리 가져오기
            history = self.sessions.get(session_id, []) if session_id else []

            # 4. LLM 호출
            response_text = await self._generate_response(
                message=message,
                context=context,
                history=history
            )

            # 5. 대화에서 메모리 추출 (자동)
            conversation_text = f"User: {message}\nAssistant: {response_text}"
            extracted_memories = await self._extract_and_save_memories(
                conversation_text,
                user_id
            )

            # 6. 세션 히스토리 업데이트
            if session_id:
                self.sessions[session_id].append({
                    "role": "user",
                    "content": message
                })
                self.sessions[session_id].append({
                    "role": "assistant",
                    "content": response_text
                })

                # 히스토리 제한 (최근 20개만 유지)
                if len(self.sessions[session_id]) > 20:
                    self.sessions[session_id] = self.sessions[session_id][-20:]

            # 7. 응답 구성
            response = {
                "response": response_text,
                "user_message": message,
                "used_memories": [
                    {
                        "id": mem.get("id"),
                        "text": mem.get("text", "")[:100] + "...",
                        "score": mem.get("score", 0)
                    }
                    for mem in relevant_memories[:3]  # 상위 3개만 표시
                ],
                "extracted_memories": extracted_memories,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"대화 처리 완료 - User: {user_id}, Session: {session_id}")
            return response

        except Exception as e:
            logger.error(f"대화 처리 실패: {e}")
            return {
                "response": "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _build_context(
        self,
        memories: List[Dict[str, Any]],
        user_id: str
    ) -> str:
        """
        메모리를 기반으로 컨텍스트 구성

        Args:
            memories: 관련 메모리 목록
            user_id: 사용자 ID

        Returns:
            str: 구성된 컨텍스트
        """
        if not memories:
            return ""

        context_parts = ["다음은 사용자에 대한 기억된 정보입니다:"]

        for i, memory in enumerate(memories[:5], 1):  # 상위 5개만 사용
            text = memory.get("text", "")
            metadata = memory.get("metadata", {})
            timestamp = metadata.get("timestamp", "")

            # 시간 정보 포맷
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%Y년 %m월 %d일")
                except:
                    time_str = "이전"
            else:
                time_str = "이전"

            context_parts.append(f"{i}. [{time_str}] {text}")

        context_parts.append("\n이 정보를 참고하여 대화해주세요.")
        return "\n".join(context_parts)

    async def _generate_response(
        self,
        message: str,
        context: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        LLM을 사용해 응답 생성

        Args:
            message: 사용자 메시지
            context: 메모리 컨텍스트
            history: 대화 히스토리

        Returns:
            str: 생성된 응답
        """
        try:
            # 메시지 구성
            messages = []

            # 시스템 프롬프트
            system_prompt = """당신은 사용자와 대화하는 친근한 AI 어시스턴트입니다.
사용자에 대한 기억된 정보를 활용하여 개인화된 대화를 진행하세요.
한국어로 자연스럽게 대화하고, 이전 대화 내용을 기억하며 일관성 있게 응답하세요."""

            messages.append({
                "role": "system",
                "content": system_prompt
            })

            # 컨텍스트 추가
            if context:
                messages.append({
                    "role": "system",
                    "content": context
                })

            # 대화 히스토리 추가 (최근 10개)
            for msg in history[-10:]:
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
            # Fallback 응답
            return "죄송합니다. 응답을 생성하는 중 문제가 발생했습니다."

    async def _extract_and_save_memories(
        self,
        conversation: str,
        user_id: str
    ) -> List[str]:
        """
        대화에서 메모리 추출 및 저장

        Args:
            conversation: 대화 내용
            user_id: 사용자 ID

        Returns:
            List[str]: 저장된 메모리 ID 목록
        """
        try:
            # LLM을 사용한 메모리 추출
            extraction_prompt = f"""다음 대화에서 기억해야 할 중요한 정보를 추출하세요.
사실, 선호도, 개인정보, 경험 등을 찾아주세요.

대화:
{conversation}

추출할 정보 (한 줄에 하나씩):"""

            response = ollama.generate(
                model=self.config.models.chat_model,
                prompt=extraction_prompt,
                options={
                    "temperature": 0.3,
                    "num_predict": 256
                }
            )

            # 추출된 정보 파싱
            extracted_text = response['response']
            memories = [
                line.strip()
                for line in extracted_text.split('\n')
                if line.strip() and not line.startswith('#')
            ]

            # 메모리 저장
            memory_ids = []
            for memory_text in memories[:5]:  # 최대 5개만 저장
                if len(memory_text) > 10:  # 너무 짧은 내용 제외
                    # 분류
                    category = await self.classifier.classify_text(memory_text)

                    # 저장
                    memory_id = await self.memory_manager.add_memory(
                        text=memory_text,
                        user_id=user_id,
                        metadata={
                            "source": "conversation",
                            "category": category,
                            "auto_extracted": True
                        }
                    )
                    memory_ids.append(memory_id)

            logger.info(f"대화에서 {len(memory_ids)}개 메모리 추출")
            return memory_ids

        except Exception as e:
            logger.error(f"메모리 추출 실패: {e}")
            return []

    def clear_session(self, session_id: str):
        """
        세션 히스토리 삭제

        Args:
            session_id: 세션 ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"세션 삭제: {session_id}")

    def get_session_history(
        self,
        session_id: str
    ) -> List[Dict[str, str]]:
        """
        세션 히스토리 가져오기

        Args:
            session_id: 세션 ID

        Returns:
            List[Dict]: 대화 히스토리
        """
        return self.sessions.get(session_id, [])