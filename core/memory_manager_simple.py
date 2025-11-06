"""
간소화된 mem0 메모리 관리 시스템
직접적인 메모리 저장 및 검색 구현
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from mem0 import Memory
from config.settings import load_config, AppConfig

logger = logging.getLogger(__name__)


class SimpleMemoryManager:
    """간소화된 메모리 매니저 - 직접 저장"""

    def __init__(self, config: Optional[AppConfig] = None):
        """초기화"""
        self.config = config or load_config()

        # data_dir 확인
        if not isinstance(self.config.data_dir, Path):
            self.config.data_dir = Path(self.config.data_dir)

        # mem0 설정 (Ollama 임베딩 사용)
        self.mem0_config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": self.config.models.chat_model,
                    "temperature": 0.7,
                    "max_tokens": 512,
                    "ollama_base_url": "http://localhost:11434"
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "nomic-embed-text",
                    "ollama_base_url": "http://localhost:11434"
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "memories",
                    "path": str(self.config.data_dir / "chroma_db")
                }
            }
        }

        # 메모리 인스턴스 생성
        try:
            # ChromaDB 디렉토리 생성
            chroma_dir = self.config.data_dir / "chroma_db"
            chroma_dir.mkdir(parents=True, exist_ok=True)

            self.memory = Memory.from_config(self.mem0_config)
            logger.info("간소화된 메모리 시스템 초기화 완료")
        except Exception as e:
            logger.error(f"메모리 초기화 실패: {e}")
            self.memory = None

        # 로컬 메모리 저장소 (백업)
        self.local_memories_file = self.config.data_dir / "local_memories.json"
        self.local_memories = self._load_local_memories()

    def _load_local_memories(self) -> Dict[str, List[Dict]]:
        """로컬 메모리 로드"""
        if self.local_memories_file.exists():
            try:
                with open(self.local_memories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_local_memories(self):
        """로컬 메모리 저장"""
        try:
            with open(self.local_memories_file, 'w', encoding='utf-8') as f:
                json.dump(self.local_memories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"로컬 메모리 저장 실패: {e}")

    async def add_memory(
        self,
        text: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """메모리 추가 (로컬 저장 포함)"""
        try:
            if metadata is None:
                metadata = {}

            # 메타데이터 추가
            metadata.update({
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source": metadata.get("source", "manual")
            })

            # 메모리 ID 생성
            memory_id = f"mem_{user_id}_{datetime.now().timestamp()}"

            # 로컬 저장
            if user_id not in self.local_memories:
                self.local_memories[user_id] = []

            memory_entry = {
                "id": memory_id,
                "text": text,
                "metadata": metadata
            }

            self.local_memories[user_id].append(memory_entry)
            self._save_local_memories()

            # mem0에도 저장 시도
            if self.memory:
                try:
                    self.memory.add(
                        messages=[{"role": "user", "content": text}],
                        user_id=user_id,
                        metadata=metadata,
                        infer=False  # 자동 번역/추론 비활성화 - 원본 언어 그대로 저장
                    )
                except Exception as e:
                    logger.warning(f"mem0 저장 실패, 로컬만 저장: {e}")

            logger.info(f"메모리 추가 완료: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"메모리 추가 실패: {e}")
            return f"error_{datetime.now().timestamp()}"

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """메모리 검색 (벡터 유사도 기반)"""
        results = []

        # mem0 검색 시도 (벡터 유사도 검색 - 최우선)
        if self.memory:
            try:
                logger.info(f"🔍 mem0 벡터 검색 시도: '{query}'")
                mem0_results = self.memory.search(query=query, user_id=user_id, limit=limit)

                if mem0_results:
                    # mem0 결과 형식: {'results': [...]}
                    if isinstance(mem0_results, dict):
                        actual_results = mem0_results.get('results', [])
                    elif isinstance(mem0_results, list):
                        actual_results = mem0_results
                    else:
                        actual_results = []

                    logger.info(f"✅ mem0 벡터 검색 성공: {len(actual_results)}개 결과")

                    # mem0 결과를 표준 형식으로 변환
                    for result in actual_results:
                        if isinstance(result, dict):
                            # mem0 반환 형식: {'id': ..., 'memory': ..., 'score': ..., 'metadata': ...}
                            results.append({
                                "id": result.get("id", ""),
                                "text": result.get("memory", result.get("text", "")),
                                "score": result.get("score", 0.9),
                                "metadata": result.get("metadata", {})
                            })
                        else:
                            # 객체 형태인 경우
                            results.append({
                                "id": getattr(result, "id", ""),
                                "text": getattr(result, "memory", getattr(result, "text", str(result))),
                                "score": getattr(result, "score", 0.9),
                                "metadata": getattr(result, "metadata", {})
                            })

                    if results:
                        logger.info(f"✅ 벡터 유사도 검색 완료: {len(results)}개")
                        logger.info(f"   예시: {results[0]['text'][:50]}...")
                        return results[:limit]
                    else:
                        logger.warning(f"⚠️ 변환된 결과 없음")
                else:
                    logger.warning(f"⚠️ mem0 검색 결과 없음")

            except Exception as e:
                logger.warning(f"⚠️ mem0 벡터 검색 실패, 로컬 검색으로 폴백: {e}")
                import traceback
                traceback.print_exc()

        # 로컬 검색 폴백 (개선된 유사도 계산)
        logger.info(f"📝 로컬 텍스트 유사도 검색 사용")
        if user_id in self.local_memories:
            query_lower = query.lower()
            query_terms = set(query_lower.split())

            scored_results = []
            for memory in self.local_memories[user_id]:
                text_lower = memory["text"].lower()
                text_terms = set(text_lower.split())

                # 유사도 점수 계산
                score = 0.0

                # 1. 완전 일치
                if query_lower in text_lower:
                    score = 0.95

                # 2. 부분 일치
                elif any(term in text_lower for term in query_terms):
                    # Jaccard 유사도 (단순 버전)
                    intersection = query_terms & text_terms
                    union = query_terms | text_terms
                    if union:
                        score = 0.5 + (0.4 * len(intersection) / len(union))

                # 임계값 적용
                if threshold and score < threshold:
                    continue

                if score > 0:
                    scored_results.append({
                        "id": memory["id"],
                        "text": memory["text"],
                        "score": score,
                        "metadata": memory["metadata"]
                    })

            # 점수 순으로 정렬
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            results = scored_results[:limit]

            logger.info(f"📝 로컬 검색 완료: {len(results)}개 결과")
        else:
            logger.warning(f"⚠️ 사용자 {user_id}의 로컬 메모리 없음")

        if not results:
            logger.warning(f"⚠️ 검색 결과 없음: '{query}'")

        return results

    async def get_all_memories(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """모든 메모리 가져오기"""
        memories = []

        # mem0에서 가져오기
        if self.memory:
            try:
                mem0_memories = self.memory.get_all(user_id=user_id)
                if mem0_memories:
                    # mem0 결과 형식 처리: {'results': [...]} 또는 리스트
                    if isinstance(mem0_memories, dict):
                        actual_memories = mem0_memories.get('results', [])
                    elif isinstance(mem0_memories, list):
                        actual_memories = mem0_memories
                    else:
                        actual_memories = []

                    # 표준 형식으로 변환
                    for mem in actual_memories:
                        if isinstance(mem, dict):
                            memories.append({
                                "id": mem.get("id", ""),
                                "text": mem.get("memory", mem.get("text", "")),
                                "metadata": mem.get("metadata", {})
                            })
                        elif isinstance(mem, str):
                            # 문자열인 경우 건너뛰기
                            logger.warning(f"문자열 메모리 발견, 건너뜀: {mem[:50]}...")
                            continue
                        else:
                            # 객체 형태
                            memories.append({
                                "id": getattr(mem, "id", ""),
                                "text": getattr(mem, "memory", getattr(mem, "text", str(mem))),
                                "metadata": getattr(mem, "metadata", {})
                            })

                    logger.info(f"mem0에서 {len(memories)}개 메모리 로드")
            except Exception as e:
                logger.warning(f"mem0 조회 실패: {e}")
                import traceback
                traceback.print_exc()

        # 로컬 메모리 추가
        if user_id in self.local_memories:
            local = self.local_memories[user_id]
            # mem0 메모리와 중복 제거
            mem0_ids = {m.get("id") for m in memories}

            for memory in local:
                if isinstance(memory, dict) and memory.get("id") not in mem0_ids:
                    memories.append(memory)

        # 제한 적용
        if limit and len(memories) > limit:
            memories = memories[:limit]

        logger.info(f"전체 메모리 조회: {len(memories)}개")
        return memories

    async def delete_memory(
        self,
        memory_id: str,
        user_id: str
    ) -> bool:
        """메모리 삭제"""
        try:
            # mem0에서 삭제
            if self.memory:
                try:
                    self.memory.delete(memory_id=memory_id)
                except:
                    pass

            # 로컬에서 삭제
            if user_id in self.local_memories:
                self.local_memories[user_id] = [
                    m for m in self.local_memories[user_id]
                    if m["id"] != memory_id
                ]
                self._save_local_memories()

            logger.info(f"메모리 삭제 완료: {memory_id}")
            return True

        except Exception as e:
            logger.error(f"메모리 삭제 실패: {e}")
            return False

    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """통계 정보"""
        memories = self.local_memories.get(user_id, [])

        categories = {}
        for mem in memories:
            category = mem.get("metadata", {}).get("category", "uncategorized")
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_memories": len(memories),
            "categories": categories,
            "last_updated": memories[-1]["metadata"]["timestamp"] if memories else "",
            "storage_type": "Local + ChromaDB"
        }