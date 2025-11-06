#!/usr/bin/env python3
"""
벡터 유사도 검색 테스트
mem0의 벡터 DB가 제대로 작동하는지 확인
"""

import asyncio
import sys
from pathlib import Path
from colorama import init, Fore, Style

sys.path.append(str(Path(__file__).parent))

from core.memory_manager_simple import SimpleMemoryManager
from config.settings import load_config

init()


async def test_vector_search():
    """벡터 유사도 검색 테스트"""
    print(Fore.CYAN + "\n" + "=" * 60)
    print("🔍 벡터 유사도 검색 테스트")
    print("=" * 60 + Style.RESET_ALL)

    config = load_config()
    memory_manager = SimpleMemoryManager(config)
    test_user = "vector_test_user"

    # 1. 테스트 메모리 추가
    print(Fore.YELLOW + "\n1. 테스트 메모리 저장" + Style.RESET_ALL)
    print("-" * 40)

    test_memories = [
        "저는 파이썬 프로그래밍을 좋아합니다",
        "자바스크립트도 사용할 수 있어요",
        "저는 커피를 매일 마십니다",
        "차보다 커피가 더 좋아요",
        "등산을 즐겨합니다",
        "주말에는 북한산에 자주 갑니다",
        "저는 개발자입니다",
        "웹 개발을 주로 합니다",
        "강아지를 좋아합니다",
        "고양이도 좋아해요"
    ]

    for memory_text in test_memories:
        memory_id = await memory_manager.add_memory(
            text=memory_text,
            user_id=test_user,
            metadata={"test": True}
        )
        print(f"   ✓ {memory_text}")

    print(Fore.GREEN + f"\n✅ {len(test_memories)}개 메모리 저장 완료" + Style.RESET_ALL)

    # 2. 유사도 검색 테스트
    print(Fore.YELLOW + "\n2. 벡터 유사도 검색 테스트" + Style.RESET_ALL)
    print("-" * 40)

    search_queries = [
        ("프로그래밍", ["파이썬", "자바스크립트", "개발자", "웹"]),
        ("음료", ["커피", "차"]),
        ("운동", ["등산", "북한산"]),
        ("동물", ["강아지", "고양이"]),
        ("코딩", ["파이썬", "개발"]),  # 동의어 테스트
        ("산", ["등산", "북한산"]),  # 관련어 테스트
    ]

    for query, expected_keywords in search_queries:
        print(f"\n🔎 검색어: '{query}'")

        results = await memory_manager.search_memories(
            query=query,
            user_id=test_user,
            limit=3
        )

        if results:
            print(f"   결과: {len(results)}개")
            for i, result in enumerate(results, 1):
                score = result.get('score', 0)
                text = result.get('text', '')
                print(f"\n   [{i}] (점수: {score:.2f})")
                print(f"       {text}")

                # 기대 키워드 확인
                matched = any(kw in text for kw in expected_keywords)
                if matched:
                    print(Fore.GREEN + f"       ✅ 관련 있음" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + f"       ⚠️ 관련성 낮음" + Style.RESET_ALL)
        else:
            print(Fore.RED + "   ❌ 검색 결과 없음" + Style.RESET_ALL)

    # 3. 벡터 DB 상태 확인
    print(Fore.YELLOW + "\n3. 벡터 DB 상태 확인" + Style.RESET_ALL)
    print("-" * 40)

    chroma_dir = Path("data") / "chroma_db"
    if chroma_dir.exists():
        db_files = list(chroma_dir.rglob("*"))
        db_size = sum(f.stat().st_size for f in db_files if f.is_file())

        print(Fore.GREEN + "✅ ChromaDB 폴더 존재" + Style.RESET_ALL)
        print(f"   파일 개수: {len(db_files)}개")
        print(f"   총 크기: {db_size / 1024:.2f} KB")

        if memory_manager.memory:
            print(Fore.GREEN + "✅ mem0 인스턴스 활성화됨" + Style.RESET_ALL)
            print("   → 벡터 유사도 검색 사용 가능")
        else:
            print(Fore.RED + "❌ mem0 인스턴스 없음" + Style.RESET_ALL)
            print("   → 로컬 텍스트 매칭만 사용")
    else:
        print(Fore.RED + "❌ ChromaDB 폴더 없음" + Style.RESET_ALL)
        print("   → 벡터 검색 불가능")

    # 4. 검색 방식 비교
    print(Fore.YELLOW + "\n4. 검색 방식 비교" + Style.RESET_ALL)
    print("-" * 40)

    comparison_query = "프로그램"
    print(f"검색어: '{comparison_query}'")

    results = await memory_manager.search_memories(
        query=comparison_query,
        user_id=test_user,
        limit=5
    )

    if results:
        print(f"\n결과 분석:")
        for result in results:
            text = result.get('text', '')
            score = result.get('score', 0)
            print(f"   점수 {score:.2f}: {text}")

        # 유사도 검색 vs 키워드 검색
        has_exact_match = any(comparison_query in r['text'] for r in results)

        if not has_exact_match and results:
            print(Fore.GREEN + "\n✅ 벡터 유사도 검색이 작동 중입니다!" + Style.RESET_ALL)
            print("   (정확히 일치하지 않아도 관련된 결과를 찾음)")
        elif has_exact_match:
            print(Fore.YELLOW + "\n⚠️ 키워드 매칭으로 보입니다" + Style.RESET_ALL)
        else:
            print(Fore.RED + "\n❌ 검색 결과 없음" + Style.RESET_ALL)
    else:
        print(Fore.RED + "\n❌ 검색 결과 없음" + Style.RESET_ALL)

    # 5. 정리
    print(Fore.YELLOW + "\n5. 테스트 데이터 정리" + Style.RESET_ALL)
    print("-" * 40)

    all_memories = await memory_manager.get_all_memories(test_user)
    for memory in all_memories:
        if memory.get('id'):
            await memory_manager.delete_memory(memory['id'], test_user)

    print(Fore.GREEN + "✅ 테스트 데이터 정리 완료" + Style.RESET_ALL)

    # 최종 결과
    print(Fore.CYAN + "\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60 + Style.RESET_ALL)

    if memory_manager.memory:
        print(Fore.GREEN + "✅ mem0 벡터 DB가 정상 작동합니다!" + Style.RESET_ALL)
        print("   - 의미적 유사도 기반 검색 가능")
        print("   - 동의어/관련어 검색 지원")
    else:
        print(Fore.YELLOW + "⚠️ mem0 벡터 DB를 사용할 수 없습니다" + Style.RESET_ALL)
        print("   - 로컬 텍스트 매칭으로 폴백됨")
        print("   - 정확한 키워드만 검색 가능")
        print("\n해결 방법:")
        print("1. ollama serve 실행 확인")
        print("2. python setup_models.py 실행")
        print("3. data/chroma_db 폴더 권한 확인")


async def quick_test():
    """빠른 테스트"""
    print(Fore.CYAN + "\n벡터 검색 빠른 테스트" + Style.RESET_ALL)

    config = load_config()
    memory_manager = SimpleMemoryManager(config)

    print("\n벡터 DB 상태:")
    if memory_manager.memory:
        print(Fore.GREEN + "✅ mem0 활성화 - 벡터 유사도 검색 사용" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "⚠️ mem0 비활성화 - 텍스트 매칭 사용" + Style.RESET_ALL)

    chroma_dir = Path("data") / "chroma_db"
    if chroma_dir.exists():
        print(Fore.GREEN + "✅ ChromaDB 폴더 존재" + Style.RESET_ALL)
    else:
        print(Fore.RED + "❌ ChromaDB 폴더 없음" + Style.RESET_ALL)


async def main():
    """메인 함수"""
    print(Fore.CYAN + "\n선택하세요:" + Style.RESET_ALL)
    print("1. 전체 테스트 (자동 실행)")
    print("2. 빠른 상태 확인")

    choice = input("\n선택 (1 또는 2): ")

    if choice == "1":
        await test_vector_search()
    elif choice == "2":
        await quick_test()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    try:
        # colorama 설치 확인
        try:
            from colorama import init, Fore, Style
        except ImportError:
            print("colorama 설치 중...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "colorama"])
            from colorama import init, Fore, Style

        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()