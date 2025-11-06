"""
mem0 기반 메모리 관리 시스템
mem0 공식 문서 참고: https://github.com/mem0ai/mem0
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import sys
import requests

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from mem0 import Memory
import ollama
from config.settings import load_config, AppConfig

logger = logging.getLogger(__name__)


class MemoryManager:
    """mem0를 활용한 메모리 관리 클래스"""

    def __init__(self, config: Optional[AppConfig] = None):
        """
        메모리 매니저 초기화

        Args:
            config: 애플리케이션 설정
        """
        self.config = config or load_config()
        self.user_memories = {}  # 사용자별 메모리 인스턴스

        # Qdrant 연결 확인
        self.use_qdrant = self._check_qdrant()

        # data_dir을 Path 객체로 확인
        if not isinstance(self.config.data_dir, Path):
            self.config.data_dir = Path(self.config.data_dir)

        # mem0 설정
        if self.use_qdrant:
            # Qdrant 사용
            self.mem0_config = {
                "llm": {
                    "provider": "ollama",
                    "config": {
                        "model": self.config.models.chat_model,
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "ollama_base_url": self.config.ollama_host
                    }
                },
                "embedder": {
                    "provider": "ollama",
                    "config": {
                        "model": self.config.models.embedding_model,
                        "ollama_base_url": self.config.ollama_host
                    }
                },
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "host": self.config.database.qdrant_host,
                        "port": self.config.database.qdrant_port,
                        "collection_name": self.config.database.collection_name,
                    }
                },
                "version": "v1.1"
            }
        else:
            # ChromaDB 폴백
            self.mem0_config = {
                "llm": {
                    "provider": "ollama",
                    "config": {
                        "model": self.config.models.chat_model,
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "ollama_base_url": self.config.ollama_host
                    }
                },
                "embedder": {
                    "provider": "ollama",
                    "config": {
                        "model": self.config.models.embedding_model,
                        "ollama_base_url": self.config.ollama_host
                    }
                },
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "collection_name": "memories",
                        "path": str(self.config.data_dir / "chroma_db")
                    }
                },
                "version": "v1.1"
            }

        # 기본 메모리 인스턴스 생성
        self._initialize_default_memory()

    def _check_qdrant(self) -> bool:
        """Qdrant 서버 연결 확인"""
        try:
            response = requests.get(
                f"http://{self.config.database.qdrant_host}:{self.config.database.qdrant_port}/",
                timeout=2
            )
            if response.status_code == 200:
                logger.info("✅ Qdrant 서버 연결 성공")
                return True
        except Exception as e:
            logger.warning(f"Qdrant 연결 실패: {e}")

        return False

    def _initialize_default_memory(self):
        """기본 메모리 인스턴스 초기화"""
        try:
            if not self.use_qdrant:
                # ChromaDB 디렉토리 생성
                chroma_dir = self.config.data_dir / "chroma_db"
                chroma_dir.mkdir(parents=True, exist_ok=True)

            self.default_memory = Memory.from_config(self.mem0_config)

            if self.use_qdrant:
                logger.info("mem0 메모리 시스템 초기화 완료 (Qdrant 사용)")
            else:
                logger.info("mem0 메모리 시스템 초기화 완료 (ChromaDB 사용)")

        except Exception as e:
            logger.error(f"mem0 초기화 실패: {e}")
            # 최소 설정으로 재시도
            try:
                # 더 간단한 설정으로 재시도
                simple_config = {
                    "vector_store": {
                        "provider": "chroma",
                        "config": {
                            "collection_name": "memories",
                            "path": "./chroma_db"
                        }
                    }
                }
                self.default_memory = Memory.from_config(simple_config)
                logger.warning("간소화된 설정으로 mem0 초기화 완료")
            except Exception as e2:
                logger.error(f"mem0 초기화 완전 실패: {e2}")
                # 메모리 없이도 기본 동작은 가능하도록
                self.default_memory = None

    def get_user_memory(self, user_id: str) -> Optional[Memory]:
        """
        사용자별 메모리 인스턴스 가져오기

        Args:
            user_id: 사용자 ID

        Returns:
            Memory: 사용자 메모리 인스턴스
        """
        if self.default_memory is None:
            logger.warning("메모리 시스템이 초기화되지 않았습니다")
            return None

        if user_id not in self.user_memories:
            # 사용자별 컬렉션 이름 생성
            user_collection = f"user_{user_id}_memories"

            user_config = self.mem0_config.copy()
            user_config["vector_store"]["config"]["collection_name"] = user_collection

            try:
                self.user_memories[user_id] = Memory.from_config(user_config)
                logger.info(f"사용자 {user_id}의 메모리 인스턴스 생성")
            except Exception as e:
                logger.error(f"사용자 메모리 생성 실패: {e}")
                return self.default_memory

        return self.user_memories[user_id]

    async def add_memory(
        self,
        text: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        메모리 추가

        Args:
            text: 저장할 텍스트
            user_id: 사용자 ID
            metadata: 추가 메타데이터

        Returns:
            str: 메모리 ID
        """
        try:
            memory = self.get_user_memory(user_id)
            if memory is None:
                logger.warning("메모리 시스템을 사용할 수 없습니다")
                return f"temp_{datetime.now().timestamp()}"

            # 메타데이터 준비
            if metadata is None:
                metadata = {}

            metadata.update({
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source": "manual" if metadata.get("source") is None else metadata["source"]
            })

            # mem0에 메모리 추가
            result = memory.add(
                text,
                user_id=user_id,
                metadata=metadata
            )

            # mem0는 리스트를 반환할 수 있음
            if isinstance(result, list):
                if result and len(result) > 0:
                    memory_id = result[0].get("id", str(datetime.now().timestamp()))
                else:
                    # 빈 리스트인 경우 임시 ID
                    memory_id = f"mem_{datetime.now().timestamp()}"
            elif isinstance(result, dict):
                memory_id = result.get("id", str(datetime.now().timestamp()))
            elif result is None:
                # None인 경우 임시 ID
                memory_id = f"mem_{datetime.now().timestamp()}"
            else:
                memory_id = str(result)

            logger.info(f"메모리 추가 완료: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"메모리 추가 실패: {e}")
            # 실패해도 임시 ID 반환
            return f"temp_{datetime.now().timestamp()}"

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        메모리 검색

        Args:
            query: 검색 쿼리
            user_id: 사용자 ID
            limit: 최대 결과 수
            threshold: 유사도 임계값

        Returns:
            List[Dict]: 검색 결과
        """
        try:
            memory = self.get_user_memory(user_id)
            if memory is None:
                return []

            # mem0 검색
            results = memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )

            # 결과가 리스트가 아닌 경우 처리
            if not isinstance(results, list):
                results = []

            # 유사도 필터링
            if threshold:
                results = [
                    r for r in results
                    if r.get("score", 0) >= threshold
                ]

            logger.info(f"메모리 검색 완료: {len(results)}개 결과")
            return results

        except Exception as e:
            logger.error(f"메모리 검색 실패: {e}")
            return []

    async def get_all_memories(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        사용자의 모든 메모리 가져오기

        Args:
            user_id: 사용자 ID
            limit: 최대 개수

        Returns:
            List[Dict]: 메모리 목록
        """
        try:
            memory = self.get_user_memory(user_id)
            if memory is None:
                return []

            # mem0에서 전체 메모리 가져오기
            all_memories = memory.get_all(user_id=user_id)

            # 결과가 None이거나 리스트가 아닌 경우 처리
            if not all_memories or not isinstance(all_memories, list):
                return []

            # 제한 적용
            if limit and len(all_memories) > limit:
                all_memories = all_memories[:limit]

            logger.info(f"전체 메모리 조회: {len(all_memories)}개")
            return all_memories

        except Exception as e:
            logger.error(f"메모리 조회 실패: {e}")
            return []

    async def update_memory(
        self,
        memory_id: str,
        text: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        메모리 업데이트

        Args:
            memory_id: 메모리 ID
            text: 새로운 텍스트
            user_id: 사용자 ID
            metadata: 새로운 메타데이터

        Returns:
            bool: 성공 여부
        """
        try:
            memory = self.get_user_memory(user_id)
            if memory is None:
                return False

            # 메타데이터 업데이트
            if metadata is None:
                metadata = {}
            metadata["updated_at"] = datetime.now().isoformat()

            # mem0 업데이트
            memory.update(
                memory_id=memory_id,
                text=text,
                metadata=metadata
            )

            logger.info(f"메모리 업데이트 완료: {memory_id}")
            return True

        except Exception as e:
            logger.error(f"메모리 업데이트 실패: {e}")
            return False

    async def delete_memory(
        self,
        memory_id: str,
        user_id: str
    ) -> bool:
        """
        메모리 삭제

        Args:
            memory_id: 메모리 ID
            user_id: 사용자 ID

        Returns:
            bool: 성공 여부
        """
        try:
            memory = self.get_user_memory(user_id)
            if memory is None:
                return False

            # mem0에서 삭제
            memory.delete(memory_id=memory_id)

            logger.info(f"메모리 삭제 완료: {memory_id}")
            return True

        except Exception as e:
            logger.error(f"메모리 삭제 실패: {e}")
            return False

    async def get_memory_by_id(
        self,
        memory_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        ID로 특정 메모리 가져오기

        Args:
            memory_id: 메모리 ID
            user_id: 사용자 ID

        Returns:
            Dict: 메모리 정보
        """
        try:
            memory = self.get_user_memory(user_id)
            if memory is None:
                return None

            # 전체 메모리에서 ID로 찾기
            all_memories = await self.get_all_memories(user_id)
            for mem in all_memories:
                if mem.get("id") == memory_id:
                    return mem

            return None

        except Exception as e:
            logger.error(f"메모리 조회 실패: {e}")
            return None

    async def get_related_memories(
        self,
        memory_id: str,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        관련 메모리 찾기

        Args:
            memory_id: 기준 메모리 ID
            user_id: 사용자 ID
            limit: 최대 개수

        Returns:
            List[Dict]: 관련 메모리 목록
        """
        try:
            # 기준 메모리 가져오기
            base_memory = await self.get_memory_by_id(memory_id, user_id)
            if not base_memory:
                return []

            # 기준 메모리의 텍스트로 유사한 메모리 검색
            related = await self.search_memories(
                query=base_memory.get("text", ""),
                user_id=user_id,
                limit=limit + 1  # 자기 자신 포함
            )

            # 자기 자신 제외
            related = [r for r in related if r.get("id") != memory_id]

            return related[:limit]

        except Exception as e:
            logger.error(f"관련 메모리 검색 실패: {e}")
            return []

    async def extract_memories_from_conversation(
        self,
        conversation: str,
        user_id: str
    ) -> List[str]:
        """
        대화에서 메모리 자동 추출

        Args:
            conversation: 대화 내용
            user_id: 사용자 ID

        Returns:
            List[str]: 추출된 메모리 ID 목록
        """
        try:
            memory = self.get_user_memory(user_id)
            if memory is None:
                return []

            # mem0의 자동 추출 기능 사용
            extracted = memory.add(
                conversation,
                user_id=user_id,
                metadata={
                    "source": "conversation",
                    "auto_extracted": True,
                    "timestamp": datetime.now().isoformat()
                }
            )

            # 추출된 메모리 ID 목록 반환
            if isinstance(extracted, list):
                return [item.get("id", str(item)) for item in extracted]
            elif isinstance(extracted, dict):
                return [extracted.get("id", str(extracted))]
            else:
                return [str(extracted)]

        except Exception as e:
            logger.error(f"대화에서 메모리 추출 실패: {e}")
            return []

    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        사용자 메모리 통계

        Args:
            user_id: 사용자 ID

        Returns:
            Dict: 통계 정보
        """
        try:
            memories = self.get_all_memories(user_id)
            if not isinstance(memories, list):
                memories = []

            # 카테고리별 분류
            categories = {}
            for mem in memories:
                metadata = mem.get("metadata", {})
                category = metadata.get("category", "uncategorized")
                categories[category] = categories.get(category, 0) + 1

            stats = {
                "total_memories": len(memories),
                "categories": categories,
                "last_updated": max(
                    (m.get("metadata", {}).get("timestamp", "") for m in memories),
                    default=""
                ) if memories else "",
                "storage_type": "Qdrant" if self.use_qdrant else "ChromaDB"
            }

            return stats

        except Exception as e:
            logger.error(f"통계 생성 실패: {e}")
            return {
                "total_memories": 0,
                "categories": {},
                "last_updated": "",
                "storage_type": "Unknown"
            }