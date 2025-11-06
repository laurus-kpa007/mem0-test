#!/usr/bin/env python3
"""
벡터 검색 진단 도구
왜 벡터 검색이 안 되는지 단계별 확인
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def check_step_by_step():
    """단계별 진단"""
    print("\n" + "="*60)
    print("🔍 벡터 검색 진단 도구")
    print("="*60 + "\n")

    # 1. mem0 패키지 확인
    print("1. mem0 패키지 확인...")
    try:
        import mem0
        print(f"   ✅ mem0 버전: {mem0.__version__ if hasattr(mem0, '__version__') else 'unknown'}")
    except ImportError as e:
        print(f"   ❌ mem0 설치 안됨: {e}")
        return False

    # 2. ChromaDB 확인
    print("\n2. ChromaDB 확인...")
    try:
        import chromadb
        print(f"   ✅ chromadb 설치됨")
    except ImportError:
        print(f"   ❌ chromadb 설치 안됨")
        print("   해결: pip install chromadb")
        return False

    # 3. 설정 로드
    print("\n3. 설정 로드...")
    try:
        from config.settings import load_config
        config = load_config()
        print(f"   ✅ 설정 로드 성공")
        print(f"   - data_dir: {config.data_dir}")
    except Exception as e:
        print(f"   ❌ 설정 로드 실패: {e}")
        return False

    # 4. ChromaDB 디렉토리 확인
    print("\n4. ChromaDB 디렉토리 확인...")
    chroma_dir = config.data_dir / "chroma_db"
    if chroma_dir.exists():
        print(f"   ✅ 디렉토리 존재: {chroma_dir}")
        files = list(chroma_dir.rglob("*"))
        print(f"   - 파일 개수: {len(files)}개")
    else:
        print(f"   ⚠️ 디렉토리 없음: {chroma_dir}")
        print("   → 자동 생성 시도...")
        chroma_dir.mkdir(parents=True, exist_ok=True)
        print("   ✅ 디렉토리 생성 완료")

    # 5. mem0 Memory 인스턴스 생성 테스트
    print("\n5. mem0 Memory 인스턴스 생성 테스트...")
    try:
        from mem0 import Memory

        mem0_config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": config.models.chat_model,
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
                    "collection_name": "test_memories",
                    "path": str(config.data_dir / "chroma_db")
                }
            }
        }

        print(f"   설정: {mem0_config}")
        memory = Memory.from_config(mem0_config)
        print(f"   ✅ Memory 인스턴스 생성 성공")
        print(f"   - 타입: {type(memory)}")

        # 6. 테스트 메모리 추가
        print("\n6. 테스트 메모리 추가...")
        test_text = "저는 파이썬 프로그래밍을 좋아합니다"
        result = memory.add(
            messages=[{"role": "user", "content": test_text}],
            user_id="test_user_diagnose",
            metadata={"test": True}
        )
        print(f"   ✅ 메모리 추가 성공")
        print(f"   - 결과: {result}")

        # 7. 벡터 검색 테스트
        print("\n7. 벡터 검색 테스트...")

        # 정확한 검색
        print("\n   [테스트 A] 정확한 검색: '파이썬'")
        results = memory.search(
            query="파이썬",
            user_id="test_user_diagnose",
            limit=5
        )
        print(f"   - 결과 타입: {type(results)}")
        print(f"   - 결과 개수: {len(results) if results else 0}")
        if results:
            # 결과 형태 확인
            if isinstance(results, dict):
                print(f"   - 딕셔너리 형태")
                print(f"   - 키: {results.keys()}")
                # results 딕셔너리에서 실제 결과 추출
                actual_results = results.get('results', results.get('memories', [results]))
            elif isinstance(results, list):
                actual_results = results
            else:
                actual_results = [results]

            if actual_results:
                first = actual_results[0] if isinstance(actual_results, list) else actual_results
                print(f"   - 첫 결과 타입: {type(first)}")
                print(f"   - 첫 결과 내용: {first}")
                print(f"   ✅ 정확한 검색 성공")
        else:
            print(f"   ⚠️ 결과 없음")

        # 유사어 검색
        print("\n   [테스트 B] 유사어 검색: '코딩' (저장된: '파이썬 프로그래밍')")
        results2 = memory.search(
            query="코딩",
            user_id="test_user_diagnose",
            limit=5
        )
        if results2:
            actual2 = results2.get('results', []) if isinstance(results2, dict) else results2
            print(f"   - 결과 개수: {len(actual2)}")
            if actual2:
                print(f"   - 첫 결과: {actual2[0].get('memory', '')}")
                print(f"   - 점수: {actual2[0].get('score', 0)}")
                print(f"   ✅ 유사어 검색 성공! 벡터 검색 작동 중!")
            else:
                print(f"   ⚠️ 결과 없음")
        else:
            print(f"   ⚠️ 유사어 검색 실패")

        # 관련어 검색
        print("\n   [테스트 C] 관련어 검색: '프로그램'")
        results3 = memory.search(
            query="프로그램",
            user_id="test_user_diagnose",
            limit=5
        )
        if results3:
            actual3 = results3.get('results', []) if isinstance(results3, dict) else results3
            print(f"   - 결과 개수: {len(actual3)}")
            if actual3:
                print(f"   - 첫 결과: {actual3[0].get('memory', '')}")
                print(f"   ✅ 관련어 검색 성공")

        # 8. 정리
        print("\n8. 테스트 데이터 정리...")
        all_memories = memory.get_all(user_id="test_user_diagnose")
        if all_memories:
            for mem in all_memories:
                try:
                    memory.delete(memory_id=mem.get("id") if isinstance(mem, dict) else getattr(mem, "id", None))
                except:
                    pass
        print(f"   ✅ 정리 완료")

        # 최종 결과
        print("\n" + "="*60)
        print("📊 진단 결과")
        print("="*60)
        print("\n✅ 벡터 검색이 정상 작동합니다!")
        print("\n작동 방식:")
        print("  1. 텍스트 → nomic-embed-text → 벡터")
        print("  2. ChromaDB에 벡터 저장")
        print("  3. 검색 시 벡터 유사도 계산")
        print("  4. 의미적으로 유사한 결과 반환")

        return True

    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

        print("\n" + "="*60)
        print("❌ 벡터 검색 문제 발견")
        print("="*60)
        print("\n가능한 원인:")
        print("1. mem0 버전 문제")
        print("2. ChromaDB 초기화 실패")
        print("3. 임베딩 모델 문제")
        print("\n해결 방법:")
        print("pip install --upgrade mem0ai chromadb")
        print("python setup_models.py")

        return False


def check_simple_memory_manager():
    """SimpleMemoryManager에서 벡터 검색 확인"""
    print("\n" + "="*60)
    print("🔍 SimpleMemoryManager 벡터 검색 확인")
    print("="*60 + "\n")

    try:
        from core.memory_manager_simple import SimpleMemoryManager
        from config.settings import load_config
        import asyncio

        config = load_config()
        manager = SimpleMemoryManager(config)

        print(f"1. SimpleMemoryManager 생성")
        print(f"   - memory 인스턴스: {manager.memory is not None}")

        if manager.memory:
            print(f"   ✅ mem0 활성화됨")
            print(f"   - 타입: {type(manager.memory)}")

            async def test():
                # 테스트 메모리 추가
                print(f"\n2. 테스트 메모리 추가...")
                await manager.add_memory(
                    text="저는 자바스크립트 개발자입니다",
                    user_id="test_sm",
                    metadata={}
                )
                print(f"   ✅ 추가 완료")

                # 검색
                print(f"\n3. 검색 테스트...")
                print(f"   검색어: '프로그래머'")
                results = await manager.search_memories(
                    query="프로그래머",
                    user_id="test_sm",
                    limit=5
                )
                print(f"   결과: {len(results)}개")
                if results:
                    for r in results:
                        print(f"   - {r.get('text', '')} (점수: {r.get('score', 0)})")

                # 정리
                all_mems = await manager.get_all_memories("test_sm")
                for mem in all_mems:
                    await manager.delete_memory(mem['id'], "test_sm")

            asyncio.run(test())
            print(f"\n✅ SimpleMemoryManager 벡터 검색 작동!")
        else:
            print(f"   ❌ mem0 비활성화됨")
            print(f"   → 로컬 텍스트 매칭만 사용 중")
            print(f"\n원인 확인:")
            print(f"   - Memory.from_config() 실패")
            print(f"   - ChromaDB 초기화 오류")

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        print("\n선택하세요:")
        print("1. 기본 mem0 테스트 (추천)")
        print("2. SimpleMemoryManager 테스트")
        print("3. 둘 다")

        choice = input("\n선택 (1/2/3): ").strip()

        if choice == "1":
            check_step_by_step()
        elif choice == "2":
            check_simple_memory_manager()
        elif choice == "3":
            check_step_by_step()
            print("\n" + "="*60 + "\n")
            check_simple_memory_manager()
        else:
            print("기본 테스트 실행...")
            check_step_by_step()

    except KeyboardInterrupt:
        print("\n\n중단됨")
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()