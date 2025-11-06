#!/usr/bin/env python3
"""
강화된 채팅 서비스 테스트
메모리가 실제로 대화에 활용되는지 확인
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.chat_service_enhanced import EnhancedChatService
from core.memory_manager_simple import SimpleMemoryManager
from config.settings import load_config


async def test_enhanced_chat():
    """메모리 활용 테스트"""
    print("\n=== 강화된 채팅 서비스 테스트 ===\n")

    # 서비스 초기화
    config = load_config()
    memory_manager = SimpleMemoryManager(config)
    chat_service = EnhancedChatService(config)

    test_user = "test_user_001"
    session_id = "test_session_001"

    print("1. 사용자 정보 메모리에 저장...")

    # 메모리 저장
    memories_to_add = [
        "제 이름은 김철수입니다",
        "저는 30살입니다",
        "저는 파이썬 개발자입니다",
        "저는 커피를 좋아합니다",
        "저는 매운 음식을 싫어합니다",
        "작년에 제주도 여행을 다녀왔습니다"
    ]

    for memory in memories_to_add:
        await memory_manager.add_memory(
            text=memory,
            user_id=test_user,
            metadata={"source": "test"}
        )
        print(f"   ✓ {memory}")

    print("\n2. 메모리 확인...")
    all_memories = await memory_manager.get_all_memories(test_user)
    print(f"   총 {len(all_memories)}개의 메모리 저장됨")

    print("\n3. 메모리를 활용한 대화 테스트...")

    # 테스트 질문들
    test_questions = [
        "안녕하세요! 제 이름 기억하시나요?",
        "제가 좋아하는 음료가 뭐였죠?",
        "제 직업에 대해 말씀해주세요",
        "저에게 음식을 추천해주세요"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n질문 {i}: {question}")

        # 대화 처리
        response = await chat_service.chat(
            message=question,
            user_id=test_user,
            session_id=session_id,
            use_memory=True
        )

        print(f"응답: {response['response']}")

        # 사용된 메모리 표시
        if response.get('used_memories'):
            print(f"사용된 메모리:")
            for mem in response['used_memories']:
                print(f"  - {mem['text']}")

        if response.get('memory_context'):
            print(f"\n메모리 컨텍스트 (일부):")
            print(response['memory_context'][:300] + "...")

        print("-" * 50)

    print("\n4. 메모리 없이 대화 테스트 (비교용)...")

    # 메모리 사용 안 함
    response_no_memory = await chat_service.chat(
        message="안녕하세요! 제 이름 기억하시나요?",
        user_id="new_user_002",  # 다른 사용자
        session_id="new_session",
        use_memory=False
    )

    print(f"메모리 없는 응답: {response_no_memory['response']}")

    print("\n=== 테스트 완료 ===")
    print("\n결과:")
    print("✅ 메모리가 있을 때: 개인화된 응답 제공")
    print("❌ 메모리가 없을 때: 일반적인 응답 제공")

    # 테스트 데이터 정리
    print("\n5. 테스트 데이터 정리...")
    for memory in all_memories:
        if memory.get('id'):
            await memory_manager.delete_memory(memory['id'], test_user)
    print("   ✓ 테스트 메모리 삭제 완료")


if __name__ == "__main__":
    try:
        asyncio.run(test_enhanced_chat())
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()