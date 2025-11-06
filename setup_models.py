#!/usr/bin/env python3
"""
Ollama 모델 설정 및 설치 스크립트
자동으로 설치된 모델을 감지하고 필요한 모델을 다운로드합니다.
"""

import sys
import subprocess
import time
from typing import List, Tuple
import logging
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from config.settings import OllamaManager, initialize_config, AppConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelSetup:
    """모델 설정 및 설치 관리"""

    # 추천 모델 우선순위
    RECOMMENDED_MODELS = {
        "chat": [
            ("qwen2.5:7b", "최고 추천 - 한국어 우수, 균형잡힌 성능"),
            ("qwen2.5:14b", "고성능 - 메모리 여유시 추천"),
            ("llama3.2:8b", "대안 - Meta 최신 모델"),
            ("mistral:7b", "경량 대안")
        ],
        "classification": [
            ("qwen2.5:3b", "추천 - 빠른 분류 작업"),
            ("llama3.2:3b", "대안 - 경량 모델"),
            ("phi3:3.8b", "대안 - MS 경량 모델")
        ],
        "embedding": [
            ("nomic-embed-text", "추천 - 효율적인 임베딩"),
            ("mxbai-embed-large", "대안 - 대용량 임베딩"),
            ("bge-large", "대안 - BAAI 임베딩")
        ],
        "fallback": [
            ("llama3.2:3b", "추천 - 안정적인 백업"),
            ("phi3:3.8b", "대안 - MS 모델"),
            ("gemma2:2b", "경량 대안")
        ]
    }

    def __init__(self):
        self.ollama = OllamaManager()

    def check_ollama_installation(self) -> bool:
        """Ollama 설치 확인"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Ollama 버전: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Ollama가 설치되어 있지 않습니다.")
            logger.info("설치 방법:")
            logger.info("  Windows: https://ollama.com/download/windows")
            logger.info("  Mac: brew install ollama")
            logger.info("  Linux: curl -fsSL https://ollama.com/install.sh | sh")
            return False

    def check_ollama_running(self) -> bool:
        """Ollama 서비스 실행 확인"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            logger.warning("Ollama 서비스가 실행되고 있지 않습니다.")
            logger.info("다음 명령으로 실행하세요: ollama serve")
            return False

    def display_installed_models(self) -> List[str]:
        """설치된 모델 표시"""
        models = self.ollama.list_models()

        if not models:
            logger.info("설치된 모델이 없습니다.")
            return []

        logger.info("\n=== 현재 설치된 모델 ===")
        model_names = []
        for model in models:
            logger.info(f"  • {model.name} ({model.size})")
            model_names.append(model.name)

        return model_names

    def suggest_models(self, installed_models: List[str]) -> dict:
        """설치되지 않은 추천 모델 제안"""
        suggestions = {}

        for category, models in self.RECOMMENDED_MODELS.items():
            not_installed = []
            for model_name, description in models:
                # 모델 이름의 기본 부분만 확인
                base_name = model_name.split(':')[0]
                if not any(base_name in installed for installed in installed_models):
                    not_installed.append((model_name, description))

            if not_installed:
                suggestions[category] = not_installed

        return suggestions

    def interactive_install(self, suggestions: dict):
        """대화형 모델 설치"""
        if not suggestions:
            logger.info("모든 추천 모델이 이미 설치되어 있습니다.")
            return

        logger.info("\n=== 추천 모델 설치 ===")

        for category, models in suggestions.items():
            logger.info(f"\n[{category.upper()} 모델]")
            for i, (model_name, description) in enumerate(models, 1):
                logger.info(f"  {i}. {model_name}: {description}")

            choice = input(f"\n{category} 모델을 설치하시겠습니까? (번호 선택, Enter로 건너뛰기): ")

            if choice.strip():
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(models):
                        model_name = models[idx][0]
                        logger.info(f"\n{model_name} 다운로드 중... (시간이 걸릴 수 있습니다)")
                        if self.ollama.pull_model(model_name):
                            logger.info(f"✅ {model_name} 설치 완료!")
                        else:
                            logger.error(f"❌ {model_name} 설치 실패")
                except ValueError:
                    logger.warning("잘못된 입력입니다.")

    def quick_install(self):
        """빠른 설치 (최소 필수 모델만)"""
        essential_models = [
            "qwen2.5:7b",        # 메인 대화 모델
            "nomic-embed-text"   # 임베딩 모델
        ]

        logger.info("\n=== 필수 모델 설치 ===")
        for model in essential_models:
            if not self.ollama.is_model_available(model):
                logger.info(f"필수 모델 다운로드: {model}")
                if self.ollama.pull_model(model):
                    logger.info(f"✅ {model} 설치 완료!")
                else:
                    logger.error(f"❌ {model} 설치 실패")
            else:
                logger.info(f"✅ {model} - 이미 설치됨")

    def verify_setup(self) -> bool:
        """설정 검증"""
        logger.info("\n=== 설정 검증 ===")

        # 설정 파일 로드
        config = initialize_config()

        # 각 모델 확인
        all_ok = True
        for model_type in ["chat_model", "embedding_model"]:
            model_name = getattr(config.models, model_type)
            if self.ollama.is_model_available(model_name):
                logger.info(f"✅ {model_type}: {model_name}")
            else:
                logger.warning(f"❌ {model_type}: {model_name} - 설치되지 않음")
                all_ok = False

        return all_ok


def main():
    """메인 실행 함수"""
    print("""
╔══════════════════════════════════════════╗
║     mem0 LTM - Ollama 모델 설정 도구     ║
╚══════════════════════════════════════════╝
    """)

    setup = ModelSetup()

    # 1. Ollama 설치 확인
    if not setup.check_ollama_installation():
        logger.error("Ollama를 먼저 설치해주세요.")
        sys.exit(1)

    # 2. Ollama 서비스 확인
    if not setup.check_ollama_running():
        logger.warning("Ollama 서비스를 실행하는 것을 권장합니다.")

    # 3. 설치된 모델 표시
    installed_models = setup.display_installed_models()

    # 4. 설치 모드 선택
    print("\n설치 모드를 선택하세요:")
    print("1. 빠른 설치 (필수 모델만)")
    print("2. 대화형 설치 (추천 모델 선택)")
    print("3. 검증만 수행")
    print("4. 종료")

    choice = input("\n선택 (1-4): ").strip()

    if choice == "1":
        setup.quick_install()
    elif choice == "2":
        suggestions = setup.suggest_models(installed_models)
        setup.interactive_install(suggestions)
    elif choice == "3":
        pass  # 검증만 수행
    elif choice == "4":
        logger.info("종료합니다.")
        sys.exit(0)
    else:
        logger.warning("잘못된 선택입니다.")

    # 5. 최종 검증
    if setup.verify_setup():
        logger.info("\n✅ 모든 설정이 완료되었습니다!")
        logger.info("이제 프로젝트를 시작할 수 있습니다.")
    else:
        logger.warning("\n⚠️ 일부 모델이 누락되었습니다.")
        logger.info("필요한 모델을 설치한 후 다시 실행하세요.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        sys.exit(1)