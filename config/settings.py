"""
mem0 LTM 프로젝트 설정 파일
Ollama 모델 자동 감지 및 설정
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OllamaModel:
    """Ollama 모델 정보"""
    name: str
    size: str
    modified: str
    digest: str

    @property
    def size_gb(self) -> float:
        """모델 크기를 GB로 변환"""
        size_str = self.size.upper()
        if 'GB' in size_str:
            return float(size_str.replace('GB', '').strip())
        elif 'MB' in size_str:
            return float(size_str.replace('MB', '').strip()) / 1024
        return 0.0


@dataclass
class ModelConfig:
    """모델 설정"""
    chat_model: str = "qwen2.5:7b"
    classification_model: str = "qwen2.5:3b"
    embedding_model: str = "nomic-embed-text"
    summary_model: str = "qwen2.5:7b"
    fallback_model: str = "llama3.2:3b"

    # 모델별 파라미터 설정
    model_params: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "default": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "num_ctx": 8192,
            "num_predict": 512,
            "stop": ["</s>", "\n\n\n"],
            "repeat_penalty": 1.1,
        },
        "chat": {
            "temperature": 0.7,
            "num_ctx": 8192,
            "num_predict": 1024,
        },
        "classification": {
            "temperature": 0.3,  # 낮은 temperature로 일관된 분류
            "num_predict": 50,
        },
        "embedding": {
            "num_ctx": 512,
        },
        "summary": {
            "temperature": 0.5,
            "num_predict": 512,
        }
    })


@dataclass
class DatabaseConfig:
    """데이터베이스 설정"""
    # Vector DB (Qdrant)
    vector_db_type: str = "qdrant"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    collection_name: str = "memories"

    # Metadata DB (SQLite/PostgreSQL)
    metadata_db_type: str = "sqlite"  # "sqlite" or "postgresql"
    sqlite_path: str = "data/metadata.db"

    # PostgreSQL 설정 (선택적)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "mem0_ltm"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    # Redis Cache (선택적)
    use_redis: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0


@dataclass
class MemoryConfig:
    """메모리 시스템 설정"""
    # 메모리 타입별 설정
    max_short_term_memories: int = 100
    max_long_term_memories: int = 10000

    # 메모리 처리 설정
    memory_chunk_size: int = 512  # 토큰 단위
    memory_overlap: int = 50  # 청크 간 오버랩

    # 검색 설정
    similarity_threshold: float = 0.7
    max_search_results: int = 10
    time_weight: float = 0.2  # 시간 가중치 (0-1)

    # 중복 제거 설정
    dedup_threshold: float = 0.9

    # 메모리 수명 설정 (일 단위)
    archive_after_days: int = 90
    delete_after_days: int = 365


@dataclass
class APIConfig:
    """API 서버 설정"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS 설정
    cors_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ])

    # 인증 설정
    enable_auth: bool = True
    jwt_secret: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # Rate limiting
    enable_rate_limit: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds


@dataclass
class AppConfig:
    """전체 애플리케이션 설정"""
    app_name: str = "mem0 LTM System"
    version: str = "1.0.0"
    environment: str = "development"  # development, staging, production

    # 경로 설정
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "logs")
    uploads_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "uploads")

    # 컴포넌트 설정
    models: ModelConfig = field(default_factory=ModelConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    api: APIConfig = field(default_factory=APIConfig)

    # Ollama 설정
    ollama_host: str = "http://localhost:11434"
    ollama_timeout: int = 120  # seconds

    def __post_init__(self):
        """초기화 후 디렉토리 생성"""
        for dir_path in [self.data_dir, self.logs_dir, self.uploads_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


class OllamaManager:
    """Ollama 모델 관리자"""

    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host

    def list_models(self) -> List[OllamaModel]:
        """설치된 Ollama 모델 목록 가져오기"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )

            models = []
            lines = result.stdout.strip().split('\n')[1:]  # 헤더 제외

            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        model = OllamaModel(
                            name=parts[0],
                            digest=parts[1],
                            size=parts[2],
                            modified=' '.join(parts[3:])
                        )
                        models.append(model)

            return models

        except subprocess.CalledProcessError as e:
            logger.error(f"Ollama 모델 목록을 가져올 수 없습니다: {e}")
            return []
        except FileNotFoundError:
            logger.error("Ollama가 설치되어 있지 않습니다")
            return []

    def is_model_available(self, model_name: str) -> bool:
        """특정 모델이 설치되어 있는지 확인"""
        models = self.list_models()
        model_names = [m.name.split(':')[0] for m in models]
        return model_name.split(':')[0] in model_names

    def pull_model(self, model_name: str) -> bool:
        """모델 다운로드"""
        try:
            logger.info(f"모델 다운로드 중: {model_name}")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"모델 다운로드 완료: {model_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"모델 다운로드 실패: {e}")
            return False

    def auto_select_models(self, config: ModelConfig) -> ModelConfig:
        """설치된 모델 중에서 자동으로 적절한 모델 선택"""
        models = self.list_models()
        model_names = [m.name for m in models]

        logger.info("설치된 Ollama 모델:")
        for model in models:
            logger.info(f"  - {model.name} ({model.size})")

        # 대화 모델 선택 (우선순위)
        chat_candidates = [
            "qwen2.5:7b", "qwen2.5:14b", "qwen2.5:3b",
            "llama3.2:8b", "llama3.2:3b", "llama3.1:8b",
            "mistral:7b", "gemma2:9b", "phi3:3.8b"
        ]

        for candidate in chat_candidates:
            if any(candidate in model for model in model_names):
                config.chat_model = candidate
                logger.info(f"대화 모델 선택: {candidate}")
                break

        # 분류 모델 선택 (가벼운 모델 우선)
        classification_candidates = [
            "qwen2.5:3b", "qwen2.5:1.5b", "llama3.2:3b",
            "phi3:3.8b", "gemma2:2b"
        ]

        for candidate in classification_candidates:
            if any(candidate in model for model in model_names):
                config.classification_model = candidate
                logger.info(f"분류 모델 선택: {candidate}")
                break
        else:
            # 분류 모델이 없으면 대화 모델 사용
            config.classification_model = config.chat_model

        # 임베딩 모델 선택
        embedding_candidates = [
            "nomic-embed-text", "mxbai-embed-large",
            "bge-large", "bge-base", "bge-small", "all-minilm"
        ]

        for candidate in embedding_candidates:
            if any(candidate in model for model in model_names):
                config.embedding_model = candidate
                logger.info(f"임베딩 모델 선택: {candidate}")
                break

        # 요약 모델 (대화 모델과 동일하게 설정)
        config.summary_model = config.chat_model

        # Fallback 모델 선택
        fallback_candidates = [
            "llama3.2:3b", "llama3.2:1b", "phi3:3.8b", "gemma2:2b"
        ]

        for candidate in fallback_candidates:
            if any(candidate in model for model in model_names):
                if candidate != config.chat_model:  # 메인 모델과 다른 것 선택
                    config.fallback_model = candidate
                    logger.info(f"Fallback 모델 선택: {candidate}")
                    break

        return config

    def ensure_required_models(self, config: ModelConfig) -> bool:
        """필수 모델이 설치되어 있는지 확인하고 필요시 다운로드"""
        required_models = [
            config.chat_model,
            config.embedding_model,
        ]

        # 선택적 모델들
        optional_models = [
            config.classification_model,
            config.summary_model,
            config.fallback_model
        ]

        all_success = True

        # 필수 모델 확인
        for model in required_models:
            if not self.is_model_available(model):
                logger.warning(f"필수 모델이 설치되어 있지 않습니다: {model}")
                if not self.pull_model(model):
                    all_success = False

        # 선택적 모델 확인 (실패해도 계속 진행)
        for model in optional_models:
            if model and not self.is_model_available(model):
                logger.info(f"선택적 모델 다운로드 시도: {model}")
                self.pull_model(model)

        return all_success


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """설정 파일 로드"""
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

            # Path 객체로 변환
            for key in ['base_dir', 'data_dir', 'logs_dir', 'uploads_dir']:
                if key in config_data and isinstance(config_data[key], str):
                    config_data[key] = Path(config_data[key])

            # models가 dict인 경우 ModelConfig 객체로 변환
            if 'models' in config_data and isinstance(config_data['models'], dict):
                config_data['models'] = ModelConfig(**config_data['models'])

            # database가 dict인 경우 DatabaseConfig 객체로 변환
            if 'database' in config_data and isinstance(config_data['database'], dict):
                config_data['database'] = DatabaseConfig(**config_data['database'])

            # memory가 dict인 경우 MemoryConfig 객체로 변환
            if 'memory' in config_data and isinstance(config_data['memory'], dict):
                config_data['memory'] = MemoryConfig(**config_data['memory'])

            # api가 dict인 경우 APIConfig 객체로 변환
            if 'api' in config_data and isinstance(config_data['api'], dict):
                config_data['api'] = APIConfig(**config_data['api'])

            return AppConfig(**config_data)

    return AppConfig()


def save_config(config: AppConfig, config_path: Optional[Path] = None):
    """설정 파일 저장"""
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"

    config_dict = asdict(config)
    # Path 객체를 문자열로 변환
    for key in ['base_dir', 'data_dir', 'logs_dir', 'uploads_dir']:
        if key in config_dict:
            config_dict[key] = str(config_dict[key])

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)


def initialize_config() -> AppConfig:
    """설정 초기화 및 모델 자동 감지"""
    logger.info("설정 초기화 중...")

    # 기본 설정 로드
    config = load_config()

    # Ollama 모델 자동 감지 및 설정
    ollama = OllamaManager(config.ollama_host)
    config.models = ollama.auto_select_models(config.models)

    # 필수 모델 확인
    if not ollama.ensure_required_models(config.models):
        logger.warning("일부 필수 모델을 설치할 수 없습니다")

    # 설정 저장
    save_config(config)

    logger.info("설정 초기화 완료")
    logger.info(f"선택된 모델:")
    logger.info(f"  대화: {config.models.chat_model}")
    logger.info(f"  분류: {config.models.classification_model}")
    logger.info(f"  임베딩: {config.models.embedding_model}")
    logger.info(f"  요약: {config.models.summary_model}")
    logger.info(f"  백업: {config.models.fallback_model}")

    return config


# 기본 설정 인스턴스
if __name__ == "__main__":
    # CLI로 실행 시 초기화
    config = initialize_config()
    print(f"\n✅ 설정이 완료되었습니다!")
    print(f"설정 파일 위치: {Path(__file__).parent / 'config.json'}")