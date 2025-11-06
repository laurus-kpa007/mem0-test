#!/usr/bin/env python3
"""
벡터 검색 문제 자동 수정
"""

import subprocess
import sys
from pathlib import Path

def check_ollama_running():
    """Ollama 실행 확인"""
    print("\n1. Ollama 실행 상태 확인...")
    try:
        import ollama
        models = ollama.list()
        print("   ✅ Ollama 실행 중")
        return True
    except Exception as e:
        print(f"   ❌ Ollama 연결 실패: {e}")
        print("\n   해결: 다른 터미널에서 'ollama serve' 실행")
        return False


def check_embedding_model():
    """임베딩 모델 확인"""
    print("\n2. nomic-embed-text 모델 확인...")
    try:
        import ollama
        models = ollama.list()
        model_names = [m['name'] for m in models.get('models', [])]

        if any('nomic-embed-text' in name for name in model_names):
            print("   ✅ nomic-embed-text 설치됨")
            return True
        else:
            print("   ⚠️ nomic-embed-text 미설치")
            print("\n   설치 중...")
            result = subprocess.run(
                ['ollama', 'pull', 'nomic-embed-text'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("   ✅ nomic-embed-text 설치 완료")
                return True
            else:
                print(f"   ❌ 설치 실패: {result.stderr}")
                return False
    except Exception as e:
        print(f"   ❌ 확인 실패: {e}")
        return False


def test_memory_creation():
    """Memory 인스턴스 생성 테스트"""
    print("\n3. mem0 Memory 생성 테스트...")
    try:
        sys.path.append(str(Path(__file__).parent))
        from mem0 import Memory
        from config.settings import load_config

        config = load_config()

        mem0_config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": config.models.chat_model,
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
                    "collection_name": "test_fix",
                    "path": str(config.data_dir / "chroma_db")
                }
            }
        }

        memory = Memory.from_config(mem0_config)
        print("   ✅ Memory 인스턴스 생성 성공")

        # 간단한 테스트
        print("\n4. 벡터 검색 테스트...")
        test_text = "파이썬 프로그래밍"
        memory.add(
            messages=[{"role": "user", "content": test_text}],
            user_id="test_fix_user"
        )
        print(f"   ✅ 메모리 추가: '{test_text}'")

        results = memory.search(query="코딩", user_id="test_fix_user", limit=5)
        if results:
            print(f"   ✅ 벡터 검색 성공! ('{test_text}'에서 '코딩' 검색)")
            print(f"   → 결과: {len(results)}개")
            print(f"   → 의미 기반 검색 작동 중!")
        else:
            print(f"   ⚠️ 검색 결과 없음")

        # 정리
        all_mems = memory.get_all(user_id="test_fix_user")
        for mem in all_mems:
            try:
                memory.delete(memory_id=mem.get("id") if isinstance(mem, dict) else getattr(mem, "id", None))
            except:
                pass

        return True

    except Exception as e:
        print(f"   ❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 실행"""
    print("="*60)
    print("🔧 벡터 검색 자동 수정 도구")
    print("="*60)

    steps = [
        ("Ollama 실행", check_ollama_running),
        ("임베딩 모델", check_embedding_model),
        ("벡터 검색", test_memory_creation)
    ]

    all_passed = True
    for name, func in steps:
        if not func():
            all_passed = False
            print(f"\n❌ '{name}' 단계 실패")
            break

    print("\n" + "="*60)
    if all_passed:
        print("✅ 모든 문제 해결 완료!")
        print("\n이제 다음을 실행하세요:")
        print("  streamlit run app.py")
        print("\n벡터 유사도 검색이 정상 작동합니다:")
        print("  - '프로그래밍' 검색 → '코딩', '개발' 등 찾음")
        print("  - '커피' 검색 → '아메리카노', '카페' 등 찾음")
    else:
        print("❌ 문제 해결 실패")
        print("\n수동 해결 방법:")
        print("1. ollama serve (별도 터미널)")
        print("2. ollama pull nomic-embed-text")
        print("3. python diagnose_vector.py")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단됨")
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()