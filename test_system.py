#!/usr/bin/env python3
"""
시스템 테스트 스크립트
mem0 LTM 시스템이 제대로 동작하는지 확인
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """필수 패키지 임포트 테스트"""
    print("1. 패키지 임포트 테스트...")
    try:
        import mem0
        print("   ✅ mem0 임포트 성공")
    except ImportError as e:
        print(f"   ❌ mem0 임포트 실패: {e}")
        return False

    try:
        import ollama
        print("   ✅ ollama 임포트 성공")
    except ImportError as e:
        print(f"   ❌ ollama 임포트 실패: {e}")
        return False

    try:
        import streamlit
        print("   ✅ streamlit 임포트 성공")
    except ImportError as e:
        print(f"   ❌ streamlit 임포트 실패: {e}")
        return False

    return True


def test_config():
    """설정 로드 테스트"""
    print("\n2. 설정 로드 테스트...")
    try:
        from config.settings import load_config
        config = load_config()

        print(f"   ✅ 설정 로드 성공")
        print(f"      - data_dir: {config.data_dir} (타입: {type(config.data_dir).__name__})")
        print(f"      - 대화 모델: {config.models.chat_model}")
        print(f"      - 임베딩 모델: {config.models.embedding_model}")

        # Path 타입 확인
        if not isinstance(config.data_dir, Path):
            print(f"   ⚠️  data_dir이 Path 타입이 아닙니다!")

        return True
    except Exception as e:
        print(f"   ❌ 설정 로드 실패: {e}")
        return False


def test_ollama():
    """Ollama 연결 테스트"""
    print("\n3. Ollama 연결 테스트...")
    try:
        import ollama
        models = ollama.list()
        print(f"   ✅ Ollama 연결 성공")
        print(f"      설치된 모델: {len(models['models'])}개")
        for model in models['models'][:3]:  # 최대 3개만 표시
            print(f"      - {model['name']}")
        return True
    except Exception as e:
        print(f"   ❌ Ollama 연결 실패: {e}")
        print("      'ollama serve' 실행을 확인하세요")
        return False


def test_memory_manager():
    """메모리 매니저 초기화 테스트"""
    print("\n4. 메모리 매니저 초기화 테스트...")
    try:
        from core.memory_manager_simple import SimpleMemoryManager
        memory_manager = SimpleMemoryManager()
        print(f"   ✅ 메모리 매니저 초기화 성공 (간소화 버전)")

        return True
    except Exception as e:
        print(f"   ❌ 메모리 매니저 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_operations():
    """메모리 기본 동작 테스트"""
    print("\n5. 메모리 동작 테스트...")
    try:
        from core.memory_manager_simple import SimpleMemoryManager
        memory_manager = SimpleMemoryManager()

        test_user_id = "test_user"
        test_text = "테스트 메모리입니다. 저는 Python을 좋아합니다."

        # 메모리 추가
        memory_id = await memory_manager.add_memory(
            text=test_text,
            user_id=test_user_id,
            metadata={"test": True}
        )
        print(f"   ✅ 메모리 추가 성공 (ID: {memory_id})")

        # 메모리 검색
        results = await memory_manager.search_memories(
            query="Python",
            user_id=test_user_id,
            limit=5
        )
        print(f"   ✅ 메모리 검색 성공 ({len(results)}개 결과)")

        # 메모리 삭제 (테스트 데이터 정리)
        if memory_id and not memory_id.startswith("temp_"):
            await memory_manager.delete_memory(memory_id, test_user_id)
            print(f"   ✅ 테스트 메모리 삭제 완료")

        return True
    except Exception as e:
        print(f"   ❌ 메모리 동작 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_service():
    """채팅 서비스 초기화 테스트"""
    print("\n6. 채팅 서비스 테스트...")
    try:
        from core.chat_service import ChatService
        chat_service = ChatService()
        print(f"   ✅ 채팅 서비스 초기화 성공")
        return True
    except Exception as e:
        print(f"   ❌ 채팅 서비스 초기화 실패: {e}")
        return False


def main():
    """메인 테스트 실행"""
    print("""
╔════════════════════════════════════════════╗
║                                            ║
║        mem0 LTM 시스템 테스트 도구        ║
║                                            ║
╚════════════════════════════════════════════╝
    """)

    all_passed = True

    # 1. 임포트 테스트
    if not test_imports():
        print("\n⚠️ 필수 패키지가 설치되지 않았습니다.")
        print("   실행: pip install -r requirements.txt")
        all_passed = False

    # 2. 설정 테스트
    if not test_config():
        print("\n⚠️ 설정 파일에 문제가 있습니다.")
        all_passed = False

    # 3. Ollama 테스트
    if not test_ollama():
        print("\n⚠️ Ollama가 실행되지 않았습니다.")
        all_passed = False

    # 4. 메모리 매니저 테스트
    if not test_memory_manager():
        print("\n⚠️ 메모리 매니저 초기화에 실패했습니다.")
        all_passed = False
    else:
        # 5. 메모리 동작 테스트
        asyncio.run(test_memory_operations())

    # 6. 채팅 서비스 테스트
    if not test_chat_service():
        print("\n⚠️ 채팅 서비스 초기화에 실패했습니다.")
        all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("✅ 모든 테스트 통과! 시스템이 정상 작동합니다.")
        print("\n실행 방법:")
        print("   streamlit run app.py")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        print("\n해결 방법:")
        print("1. 가상환경이 활성화되어 있는지 확인")
        print("2. pip install -r requirements.txt 실행")
        print("3. ollama serve 실행")
        print("4. python setup_models.py 실행")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()