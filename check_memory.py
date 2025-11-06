#!/usr/bin/env python3
"""
메모리 저장 상태 확인 도구
실제로 메모리가 저장되었는지 확인합니다
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style

init()

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))


def check_local_memories():
    """로컬 메모리 파일 확인"""
    print(Fore.CYAN + "\n" + "=" * 60)
    print("🔍 메모리 저장 상태 확인 도구")
    print("=" * 60 + Style.RESET_ALL)

    # 1. 로컬 메모리 파일 확인
    data_dir = Path("data")
    memories_file = data_dir / "local_memories.json"

    print(Fore.YELLOW + "\n1. 로컬 메모리 파일 확인" + Style.RESET_ALL)
    print("-" * 40)

    if not memories_file.exists():
        print(Fore.RED + f"❌ 메모리 파일이 없습니다: {memories_file}" + Style.RESET_ALL)
        print("\n해결 방법:")
        print("1. data 폴더 생성 확인")
        print("2. 한 번이라도 대화를 시도해보세요")
        return False

    print(Fore.GREEN + f"✅ 메모리 파일 존재: {memories_file}" + Style.RESET_ALL)

    # 파일 크기 확인
    file_size = memories_file.stat().st_size
    print(f"   파일 크기: {file_size} bytes")

    if file_size == 0:
        print(Fore.RED + "   ⚠️ 파일이 비어있습니다!" + Style.RESET_ALL)
        return False

    # 2. 메모리 내용 확인
    print(Fore.YELLOW + "\n2. 저장된 메모리 내용" + Style.RESET_ALL)
    print("-" * 40)

    try:
        with open(memories_file, 'r', encoding='utf-8') as f:
            memories_data = json.load(f)

        if not memories_data:
            print(Fore.RED + "❌ 메모리가 비어있습니다" + Style.RESET_ALL)
            return False

        # 사용자별 메모리 출력
        total_memories = 0
        for user_id, user_memories in memories_data.items():
            print(f"\n👤 사용자: {user_id}")
            print(f"   메모리 개수: {len(user_memories)}개")

            if user_memories:
                print("\n   최근 메모리 (최대 5개):")
                for i, memory in enumerate(user_memories[-5:], 1):
                    print(f"\n   [{i}]")
                    print(f"   📝 내용: {memory.get('text', 'N/A')}")
                    print(f"   🆔 ID: {memory.get('id', 'N/A')}")

                    metadata = memory.get('metadata', {})
                    if metadata:
                        print(f"   📂 카테고리: {metadata.get('category', 'N/A')}")
                        print(f"   🕐 시간: {metadata.get('timestamp', 'N/A')}")
                        print(f"   📌 출처: {metadata.get('source', 'N/A')}")
                        if metadata.get('auto_extracted'):
                            print(f"   🤖 자동 추출됨")

                total_memories += len(user_memories)

        print(Fore.GREEN + f"\n✅ 총 {total_memories}개의 메모리가 저장되어 있습니다" + Style.RESET_ALL)
        return True

    except json.JSONDecodeError as e:
        print(Fore.RED + f"❌ JSON 파싱 오류: {e}" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"❌ 파일 읽기 오류: {e}" + Style.RESET_ALL)
        return False


def check_chroma_db():
    """ChromaDB 상태 확인"""
    print(Fore.YELLOW + "\n3. ChromaDB 상태 확인" + Style.RESET_ALL)
    print("-" * 40)

    chroma_dir = Path("data") / "chroma_db"

    if not chroma_dir.exists():
        print(Fore.RED + f"❌ ChromaDB 폴더가 없습니다: {chroma_dir}" + Style.RESET_ALL)
        return False

    print(Fore.GREEN + f"✅ ChromaDB 폴더 존재: {chroma_dir}" + Style.RESET_ALL)

    # ChromaDB 파일들 확인
    db_files = list(chroma_dir.glob("**/*"))
    if db_files:
        print(f"   파일 개수: {len(db_files)}개")
        # 일부 파일 표시
        for file in db_files[:5]:
            if file.is_file():
                print(f"   - {file.name} ({file.stat().st_size} bytes)")
    else:
        print(Fore.YELLOW + "   ⚠️ ChromaDB가 비어있습니다" + Style.RESET_ALL)

    return True


def check_config():
    """설정 확인"""
    print(Fore.YELLOW + "\n4. 설정 확인" + Style.RESET_ALL)
    print("-" * 40)

    config_file = Path("config") / "config.json"

    if not config_file.exists():
        print(Fore.RED + f"❌ 설정 파일이 없습니다: {config_file}" + Style.RESET_ALL)
        print("\n해결 방법:")
        print("python setup_models.py 실행")
        return False

    print(Fore.GREEN + f"✅ 설정 파일 존재" + Style.RESET_ALL)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"   채팅 모델: {config.get('models', {}).get('chat_model', 'N/A')}")
        print(f"   임베딩 모델: {config.get('models', {}).get('embedding_model', 'N/A')}")
        return True

    except Exception as e:
        print(Fore.RED + f"❌ 설정 파일 읽기 오류: {e}" + Style.RESET_ALL)
        return False


def test_memory_save():
    """메모리 저장 테스트"""
    print(Fore.YELLOW + "\n5. 메모리 저장 테스트" + Style.RESET_ALL)
    print("-" * 40)

    import asyncio
    from core.memory_manager_simple import SimpleMemoryManager
    from config.settings import load_config

    try:
        config = load_config()
        memory_manager = SimpleMemoryManager(config)

        test_user = "test_check_user"
        test_text = f"테스트 메모리 - {datetime.now().isoformat()}"

        async def save_test():
            memory_id = await memory_manager.add_memory(
                text=test_text,
                user_id=test_user,
                metadata={"test": True, "timestamp": datetime.now().isoformat()}
            )
            return memory_id

        memory_id = asyncio.run(save_test())

        if memory_id and not memory_id.startswith("error"):
            print(Fore.GREEN + f"✅ 메모리 저장 성공: {memory_id}" + Style.RESET_ALL)

            # 저장 확인
            memories_file = Path("data") / "local_memories.json"
            with open(memories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if test_user in data:
                    saved = any(m['text'] == test_text for m in data[test_user])
                    if saved:
                        print(Fore.GREEN + "✅ 파일에 실제로 저장됨 확인" + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "❌ 메모리 ID는 반환되었지만 파일에 없음" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ 사용자 데이터가 없음" + Style.RESET_ALL)

            # 테스트 데이터 정리
            async def cleanup():
                await memory_manager.delete_memory(memory_id, test_user)

            asyncio.run(cleanup())
            print("   테스트 데이터 정리 완료")
            return True
        else:
            print(Fore.RED + f"❌ 메모리 저장 실패: {memory_id}" + Style.RESET_ALL)
            return False

    except Exception as e:
        print(Fore.RED + f"❌ 테스트 중 오류: {e}" + Style.RESET_ALL)
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 실행"""
    print(Fore.CYAN + "\n메모리 시스템 진단을 시작합니다..." + Style.RESET_ALL)

    results = []

    # 1. 로컬 메모리 확인
    results.append(("로컬 메모리", check_local_memories()))

    # 2. ChromaDB 확인
    results.append(("ChromaDB", check_chroma_db()))

    # 3. 설정 확인
    results.append(("설정 파일", check_config()))

    # 4. 저장 테스트
    results.append(("메모리 저장", test_memory_save()))

    # 결과 요약
    print(Fore.CYAN + "\n" + "=" * 60)
    print("📊 진단 결과 요약")
    print("=" * 60 + Style.RESET_ALL)

    all_passed = True
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if not result:
            all_passed = False

    if all_passed:
        print(Fore.GREEN + "\n✅ 모든 검사 통과! 메모리 시스템이 정상입니다." + Style.RESET_ALL)
    else:
        print(Fore.RED + "\n❌ 일부 문제가 발견되었습니다." + Style.RESET_ALL)
        print("\n해결 방법:")
        print("1. ollama serve 실행 확인")
        print("2. python setup_models.py 실행")
        print("3. data 폴더 쓰기 권한 확인")
        print("4. 로그 파일 확인: logs/app.log")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n진단 중단됨")
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()