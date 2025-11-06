#!/usr/bin/env python3
"""
Qdrant 벡터 데이터베이스 설치 및 실행 도구
mem0와 함께 사용하기 위한 Qdrant 로컬 설정
"""

import os
import sys
import subprocess
import platform
import time
import requests
from pathlib import Path
import zipfile
import tarfile
import shutil


class QdrantInstaller:
    """Qdrant 설치 및 관리"""

    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.qdrant_dir = Path("qdrant")
        self.storage_dir = Path("qdrant_storage")

    def check_docker(self):
        """Docker 설치 확인"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Docker 설치됨: {result.stdout.strip()}")
            return True
        except:
            return False

    def run_qdrant_docker(self):
        """Docker로 Qdrant 실행"""
        print("\n🐳 Docker로 Qdrant 실행 중...")

        # 기존 컨테이너 중지 및 삭제
        subprocess.run(["docker", "stop", "qdrant"], capture_output=True)
        subprocess.run(["docker", "rm", "qdrant"], capture_output=True)

        # Qdrant 컨테이너 실행
        cmd = [
            "docker", "run", "-d",
            "--name", "qdrant",
            "-p", "6333:6333",
            "-p", "6334:6334",
            "-v", f"{self.storage_dir.absolute()}:/qdrant/storage:z",
            "qdrant/qdrant"
        ]

        try:
            subprocess.run(cmd, check=True)
            print("✅ Qdrant Docker 컨테이너 시작됨")
            print("   주소: http://localhost:6333")
            print("   대시보드: http://localhost:6333/dashboard")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker 실행 실패: {e}")
            return False

    def download_qdrant_binary(self):
        """Qdrant 바이너리 다운로드"""
        print("\n📥 Qdrant 바이너리 다운로드 중...")

        # OS별 다운로드 URL
        base_url = "https://github.com/qdrant/qdrant/releases/download/v1.7.4"

        if self.system == "windows":
            filename = "qdrant-x86_64-pc-windows-msvc.zip"
            url = f"{base_url}/{filename}"
        elif self.system == "darwin":  # macOS
            if "arm" in self.machine or "aarch64" in self.machine:
                filename = "qdrant-aarch64-apple-darwin.tar.gz"
            else:
                filename = "qdrant-x86_64-apple-darwin.tar.gz"
            url = f"{base_url}/{filename}"
        else:  # Linux
            filename = "qdrant-x86_64-unknown-linux-musl.tar.gz"
            url = f"{base_url}/{filename}"

        # 다운로드
        local_file = Path(filename)
        if not local_file.exists():
            print(f"   다운로드: {url}")
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(local_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"   진행: {percent:.1f}%", end='\r')

                print(f"\n✅ 다운로드 완료: {local_file}")
            except Exception as e:
                print(f"❌ 다운로드 실패: {e}")
                return False
        else:
            print(f"✅ 이미 다운로드됨: {local_file}")

        # 압축 해제
        print("📦 압축 해제 중...")
        self.qdrant_dir.mkdir(exist_ok=True)

        try:
            if filename.endswith('.zip'):
                with zipfile.ZipFile(local_file, 'r') as zip_ref:
                    zip_ref.extractall(self.qdrant_dir)
            else:  # tar.gz
                with tarfile.open(local_file, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.qdrant_dir)

            print("✅ 압축 해제 완료")
            return True
        except Exception as e:
            print(f"❌ 압축 해제 실패: {e}")
            return False

    def run_qdrant_binary(self):
        """Qdrant 바이너리 실행"""
        print("\n🚀 Qdrant 바이너리 실행 중...")

        # 실행 파일 찾기
        if self.system == "windows":
            qdrant_exe = self.qdrant_dir / "qdrant.exe"
        else:
            qdrant_exe = self.qdrant_dir / "qdrant"

        if not qdrant_exe.exists():
            print(f"❌ Qdrant 실행 파일을 찾을 수 없습니다: {qdrant_exe}")
            return False

        # 실행 권한 부여 (Unix 계열)
        if self.system != "windows":
            os.chmod(qdrant_exe, 0o755)

        # 저장 디렉토리 생성
        self.storage_dir.mkdir(exist_ok=True)

        # Qdrant 실행
        env = os.environ.copy()
        env["QDRANT__STORAGE__PATH"] = str(self.storage_dir.absolute())

        try:
            print(f"   실행: {qdrant_exe}")
            print(f"   저장 경로: {self.storage_dir.absolute()}")
            print("\n⭐ Qdrant가 실행됩니다. 이 창을 닫지 마세요!")
            print("   주소: http://localhost:6333")
            print("   대시보드: http://localhost:6333/dashboard")
            print("\n   종료하려면 Ctrl+C를 누르세요.")

            subprocess.run([str(qdrant_exe)], env=env)
        except KeyboardInterrupt:
            print("\n\n✅ Qdrant 종료됨")
        except Exception as e:
            print(f"❌ 실행 실패: {e}")
            return False

        return True

    def check_qdrant_running(self):
        """Qdrant 실행 상태 확인"""
        try:
            response = requests.get("http://localhost:6333/", timeout=2)
            if response.status_code == 200:
                print("✅ Qdrant가 이미 실행 중입니다!")
                print("   주소: http://localhost:6333")
                print("   대시보드: http://localhost:6333/dashboard")
                return True
        except:
            pass
        return False

    def install_qdrant_python(self):
        """Python 클라이언트 설치"""
        print("\n📦 Qdrant Python 클라이언트 설치 중...")

        if sys.platform == "win32":
            pip_cmd = [sys.executable, "-m", "pip"]
        else:
            pip_cmd = ["pip3"]

        try:
            subprocess.run(
                pip_cmd + ["install", "qdrant-client"],
                check=True
            )
            print("✅ Qdrant 클라이언트 설치 완료")
            return True
        except:
            print("❌ Qdrant 클라이언트 설치 실패")
            return False


def main():
    """메인 실행"""
    print("""
╔════════════════════════════════════════════╗
║                                            ║
║       🎯 Qdrant 벡터 DB 설치 도구 🎯      ║
║                                            ║
║        mem0와 함께 사용하기 위한           ║
║        Qdrant 로컬 설치 및 실행           ║
║                                            ║
╚════════════════════════════════════════════╝
    """)

    installer = QdrantInstaller()

    # 1. 이미 실행 중인지 확인
    if installer.check_qdrant_running():
        print("\n이미 Qdrant가 실행 중이므로 추가 작업이 필요 없습니다!")
        return

    # 2. 설치 방법 선택
    print("\n설치 방법을 선택하세요:")
    print("1. Docker로 실행 (권장)")
    print("2. 바이너리 다운로드 및 실행")
    print("3. Python 클라이언트만 설치")
    print("4. 종료")

    choice = input("\n선택 (1-4): ").strip()

    if choice == "1":
        # Docker 확인
        if not installer.check_docker():
            print("❌ Docker가 설치되어 있지 않습니다.")
            print("   Docker Desktop을 먼저 설치하세요:")
            print("   https://www.docker.com/products/docker-desktop")

            use_binary = input("\n대신 바이너리를 다운로드하시겠습니까? (y/n): ")
            if use_binary.lower() == 'y':
                if installer.download_qdrant_binary():
                    installer.run_qdrant_binary()
        else:
            installer.run_qdrant_docker()

    elif choice == "2":
        if installer.download_qdrant_binary():
            installer.run_qdrant_binary()

    elif choice == "3":
        installer.install_qdrant_python()

    elif choice == "4":
        print("종료합니다.")
        return

    # Python 클라이언트 설치 확인
    print("\n")
    installer.install_qdrant_python()

    print("\n" + "="*50)
    print("✅ 설정 완료!")
    print("\n다음 단계:")
    print("1. 새 터미널/CMD 창을 열어 Qdrant 실행")
    print("2. 다른 창에서 앱 실행: streamlit run app.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n종료합니다.")
    except Exception as e:
        print(f"오류: {e}")