#!/usr/bin/env python3
"""
초보자를 위한 간단한 설치 도구
모든 설정을 자동으로 처리합니다.
"""

import os
import sys
import subprocess
import time
from pathlib import Path


class ColorPrint:
    """컬러 출력 헬퍼"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def success(text):
        print(f"{ColorPrint.OKGREEN}✅ {text}{ColorPrint.ENDC}")

    @staticmethod
    def info(text):
        print(f"{ColorPrint.OKCYAN}ℹ️  {text}{ColorPrint.ENDC}")

    @staticmethod
    def warning(text):
        print(f"{ColorPrint.WARNING}⚠️  {text}{ColorPrint.ENDC}")

    @staticmethod
    def error(text):
        print(f"{ColorPrint.FAIL}❌ {text}{ColorPrint.ENDC}")

    @staticmethod
    def header(text):
        print(f"\n{ColorPrint.HEADER}{ColorPrint.BOLD}{text}{ColorPrint.ENDC}")


def run_command(command, shell=True, check=True):
    """명령어 실행"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)


def check_python():
    """Python 버전 확인"""
    ColorPrint.header("1. Python 확인")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 9:
        ColorPrint.success(f"Python {python_version.major}.{python_version.minor} 설치됨")
        return True
    else:
        ColorPrint.error(f"Python 3.9 이상이 필요합니다. (현재: {python_version.major}.{python_version.minor})")
        return False


def create_venv():
    """가상환경 생성"""
    ColorPrint.header("2. 가상환경 설정")

    venv_path = Path("venv")
    if venv_path.exists():
        ColorPrint.info("가상환경이 이미 존재합니다")
        return True

    ColorPrint.info("가상환경 생성 중...")
    success, _ = run_command(f"{sys.executable} -m venv venv")

    if success:
        ColorPrint.success("가상환경 생성 완료")
        return True
    else:
        ColorPrint.error("가상환경 생성 실패")
        return False


def install_packages():
    """패키지 설치"""
    ColorPrint.header("3. 패키지 설치")

    # 가상환경 Python 경로
    if sys.platform == "win32":
        pip_path = Path("venv/Scripts/pip.exe")
    else:
        pip_path = Path("venv/bin/pip")

    if not pip_path.exists():
        ColorPrint.error("가상환경 pip를 찾을 수 없습니다")
        return False

    # pip 업그레이드
    ColorPrint.info("pip 업그레이드 중...")
    run_command(f"{pip_path} install --upgrade pip", check=False)

    # 필수 패키지만 먼저 설치 (빠른 시작을 위해)
    essential_packages = [
        "streamlit",
        "mem0ai",
        "ollama",
        "chromadb",  # Qdrant 대신 더 간단한 벡터 DB
    ]

    for package in essential_packages:
        ColorPrint.info(f"{package} 설치 중...")
        success, _ = run_command(f"{pip_path} install {package}", check=False)
        if success:
            ColorPrint.success(f"{package} 설치 완료")
        else:
            ColorPrint.warning(f"{package} 설치 실패 (나중에 재시도)")

    # 나머지 패키지 설치
    ColorPrint.info("전체 패키지 설치 중... (5-10분 소요)")
    success, _ = run_command(f"{pip_path} install -r requirements.txt", check=False)

    if success:
        ColorPrint.success("모든 패키지 설치 완료")
    else:
        ColorPrint.warning("일부 패키지 설치 실패 (프로그램은 실행 가능)")

    return True


def check_ollama():
    """Ollama 설치 확인"""
    ColorPrint.header("4. Ollama 확인")

    success, output = run_command("ollama --version", check=False)

    if success:
        ColorPrint.success("Ollama 설치됨")
        return True
    else:
        ColorPrint.warning("Ollama가 설치되지 않았습니다")
        ColorPrint.info("Ollama 설치 방법:")
        ColorPrint.info("  Windows: https://ollama.com/download/windows")
        ColorPrint.info("  Mac: brew install ollama")
        ColorPrint.info("  Linux: curl -fsSL https://ollama.com/install.sh | sh")

        response = input("\nOllama 없이 계속하시겠습니까? (y/n): ")
        return response.lower() == 'y'


def download_models():
    """모델 다운로드"""
    ColorPrint.header("5. AI 모델 설치")

    # Ollama 실행 확인
    success, _ = run_command("ollama list", check=False)
    if not success:
        ColorPrint.warning("Ollama가 실행되지 않았습니다")
        ColorPrint.info("새 터미널에서 'ollama serve' 실행 후 Enter를 누르세요")
        input("계속하려면 Enter...")

    # 필수 모델 다운로드
    models = [
        ("qwen2.5:7b", "대화 모델 (4GB)"),
        ("nomic-embed-text", "임베딩 모델 (274MB)")
    ]

    for model, description in models:
        ColorPrint.info(f"{description} 다운로드 중...")
        ColorPrint.info("(인터넷 속도에 따라 5-20분 소요)")

        success, _ = run_command(f"ollama pull {model}", check=False)

        if success:
            ColorPrint.success(f"{model} 다운로드 완료")
        else:
            ColorPrint.warning(f"{model} 다운로드 실패 (나중에 재시도 가능)")

    return True


def create_shortcuts():
    """실행 파일 생성"""
    ColorPrint.header("6. 실행 파일 생성")

    # Windows 배치 파일
    if sys.platform == "win32":
        if not Path("start.bat").exists():
            ColorPrint.info("Windows 실행 파일이 이미 생성되어 있습니다")
        ColorPrint.success("start.bat 파일로 실행 가능")

    # Mac/Linux 쉘 스크립트
    else:
        if Path("start.sh").exists():
            os.chmod("start.sh", 0o755)
            ColorPrint.success("start.sh 파일로 실행 가능")


def main():
    """메인 설치 프로세스"""
    print("""
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║     🧠 mem0 LTM 간단 설치 도구 🧠         ║
    ║                                            ║
    ║     초보자를 위한 자동 설치 프로그램        ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """)

    ColorPrint.info("설치를 시작합니다...")
    time.sleep(2)

    # 설치 단계
    steps = [
        ("Python 확인", check_python),
        ("가상환경 생성", create_venv),
        ("패키지 설치", install_packages),
        ("Ollama 확인", check_ollama),
        ("AI 모델 다운로드", download_models),
        ("실행 파일 생성", create_shortcuts)
    ]

    failed = False
    for step_name, step_func in steps:
        if not step_func():
            ColorPrint.error(f"{step_name} 실패")
            failed = True
            break

    print("\n" + "="*50)

    if not failed:
        ColorPrint.success("🎉 설치 완료!")
        print("\n실행 방법:")

        if sys.platform == "win32":
            print("  1. start.bat 파일 더블클릭")
            print("  또는")
            print("  2. 명령 프롬프트에서: start.bat")
        else:
            print("  1. 터미널에서: ./start.sh")
            print("  또는")
            print("  2. 터미널에서: streamlit run app.py")

        print("\n브라우저에서 http://localhost:8501 접속")

    else:
        ColorPrint.error("설치 중 오류가 발생했습니다")
        ColorPrint.info("README.md 파일의 문제 해결 섹션을 참조하세요")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ColorPrint.warning("\n설치가 중단되었습니다")
    except Exception as e:
        ColorPrint.error(f"오류 발생: {e}")
        sys.exit(1)