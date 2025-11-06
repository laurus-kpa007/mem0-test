#!/usr/bin/env python3
"""
mem0 LTM 빠른 데모
메모리가 실제로 작동하는 것을 보여주는 간단한 데모
"""

import asyncio
import sys
from pathlib import Path
from colorama import init, Fore, Style

sys.path.append(str(Path(__file__).parent))

from core.chat_service_enhanced import EnhancedChatService
from core.memory_manager_simple import SimpleMemoryManager
from config.settings import load_config

# colorama 초기화
init()


async def quick_demo():
    """빠른 데모 실행"""
    print(Fore.CYAN + "\n" + "=" * 60)
    print("🧠 mem0 LTM 빠른 데모 - 메모리가 작동하는 것을 확인하세요!")
    print("=" * 60 + Style.RESET_ALL)

    # 서비스 초기화
    config = load_config()
    memory_manager = SimpleMemoryManager(config)
    chat_service = EnhancedChatService(config)

    demo_user = "demo_user"
    session_id = "demo_session"

    print(Fore.YELLOW + "\n📝 시나리오 1: 자기소개" + Style.RESET_ALL)
    print("-" * 40)

    # 첫 번째 대화 - 자기소개
    intro_message = "안녕하세요! 저는 이영희입니다. 28살이고 UX 디자이너로 일하고 있어요. 커피를 정말 좋아해서 매일 아침 카페라떼를 마셔요."

    print(f"\n👤 사용자: {intro_message}")

    response1 = await chat_service.chat(
        message=intro_message,
        user_id=demo_user,
        session_id=session_id,
        use_memory=True
    )

    print(f"\n🤖 AI: {response1['response']}")

    if response1.get('used_memories'):
        print(Fore.GREEN + "\n✅ 자동 저장된 정보:" + Style.RESET_ALL)
        memories = await memory_manager.get_all_memories(demo_user)
        for mem in memories[-5:]:  # 최근 5개
            print(f"   - {mem['text']}")

    # 잠시 대기
    await asyncio.sleep(2)

    print(Fore.YELLOW + "\n\n📝 시나리오 2: 기억 확인" + Style.RESET_ALL)
    print("-" * 40)

    # 두 번째 대화 - 이름 확인
    check_message = "제 이름 기억하시나요?"

    print(f"\n👤 사용자: {check_message}")

    response2 = await chat_service.chat(
        message=check_message,
        user_id=demo_user,
        session_id=session_id,
        use_memory=True
    )

    print(f"\n🤖 AI: {response2['response']}")

    if response2.get('used_memories'):
        print(Fore.GREEN + "\n✅ 사용된 메모리:" + Style.RESET_ALL)
        for mem in response2['used_memories']:
            print(f"   - {mem['text']}")

    # 잠시 대기
    await asyncio.sleep(2)

    print(Fore.YELLOW + "\n\n📝 시나리오 3: 선호도 기반 추천" + Style.RESET_ALL)
    print("-" * 40)

    # 세 번째 대화 - 추천 요청
    recommend_message = "아침에 뭘 마시면 좋을까요? 추천해주세요."

    print(f"\n👤 사용자: {recommend_message}")

    response3 = await chat_service.chat(
        message=recommend_message,
        user_id=demo_user,
        session_id=session_id,
        use_memory=True
    )

    print(f"\n🤖 AI: {response3['response']}")

    if response3.get('used_memories'):
        print(Fore.GREEN + "\n✅ 참조한 메모리:" + Style.RESET_ALL)
        for mem in response3['used_memories']:
            print(f"   - {mem['text']}")

    # 잠시 대기
    await asyncio.sleep(2)

    print(Fore.YELLOW + "\n\n📝 시나리오 4: 직업 관련 대화" + Style.RESET_ALL)
    print("-" * 40)

    # 네 번째 대화 - 직업 관련
    job_message = "제 직업과 관련된 팁을 주세요."

    print(f"\n👤 사용자: {job_message}")

    response4 = await chat_service.chat(
        message=job_message,
        user_id=demo_user,
        session_id=session_id,
        use_memory=True
    )

    print(f"\n🤖 AI: {response4['response']}")

    if response4.get('used_memories'):
        print(Fore.GREEN + "\n✅ 활용한 메모리:" + Style.RESET_ALL)
        for mem in response4['used_memories']:
            print(f"   - {mem['text']}")

    # 결과 요약
    print(Fore.CYAN + "\n\n" + "=" * 60)
    print("📊 데모 결과 요약")
    print("=" * 60 + Style.RESET_ALL)

    all_memories = await memory_manager.get_all_memories(demo_user)

    print(f"\n총 저장된 메모리: {len(all_memories)}개")

    categories = {}
    for mem in all_memories:
        cat = mem.get('metadata', {}).get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1

    print("\n카테고리별 분류:")
    for cat, count in categories.items():
        print(f"   - {cat}: {count}개")

    print(Fore.GREEN + "\n✅ mem0가 성공적으로 작동합니다!" + Style.RESET_ALL)
    print("   • 대화에서 자동으로 정보 추출")
    print("   • 메모리를 활용한 개인화된 응답")
    print("   • 선호도 기반 추천")
    print("   • 직업 정보 활용")

    # 정리
    print(Fore.YELLOW + "\n\n🧹 데모 데이터 정리 중..." + Style.RESET_ALL)
    for memory in all_memories:
        if memory.get('id'):
            await memory_manager.delete_memory(memory['id'], demo_user)

    print(Fore.GREEN + "✅ 정리 완료!" + Style.RESET_ALL)


async def interactive_demo():
    """대화형 데모"""
    print(Fore.CYAN + "\n" + "=" * 60)
    print("🧠 mem0 LTM 대화형 데모")
    print("=" * 60 + Style.RESET_ALL)

    # 서비스 초기화
    config = load_config()
    memory_manager = SimpleMemoryManager(config)
    chat_service = EnhancedChatService(config)

    demo_user = "interactive_user"
    session_id = "interactive_session"

    print(Fore.YELLOW + "\n💬 대화를 시작하세요! (종료: 'quit' 입력)" + Style.RESET_ALL)
    print("예시: '저는 홍길동입니다', '저는 개발자입니다', '제 이름 아세요?'\n")

    while True:
        user_input = input(Fore.CYAN + "You: " + Style.RESET_ALL)

        if user_input.lower() in ['quit', 'exit', '종료']:
            break

        response = await chat_service.chat(
            message=user_input,
            user_id=demo_user,
            session_id=session_id,
            use_memory=True
        )

        print(Fore.GREEN + f"AI: {response['response']}" + Style.RESET_ALL)

        if response.get('used_memories'):
            print(Fore.YELLOW + "   [사용된 메모리: ", end="")
            for i, mem in enumerate(response['used_memories']):
                if i > 0:
                    print(", ", end="")
                print(f"'{mem['text'][:30]}...'", end="")
            print("]" + Style.RESET_ALL)

        print()  # 줄바꿈

    # 정리
    print(Fore.YELLOW + "\n정리 중..." + Style.RESET_ALL)
    all_memories = await memory_manager.get_all_memories(demo_user)
    for memory in all_memories:
        if memory.get('id'):
            await memory_manager.delete_memory(memory['id'], demo_user)

    print(Fore.GREEN + "데모 종료!" + Style.RESET_ALL)


async def main():
    """메인 함수"""
    print(Fore.CYAN + "\n어떤 데모를 실행하시겠습니까?" + Style.RESET_ALL)
    print("1. 자동 데모 (시나리오 자동 실행)")
    print("2. 대화형 데모 (직접 대화)")

    choice = input("\n선택 (1 또는 2): ")

    if choice == "1":
        await quick_demo()
    elif choice == "2":
        await interactive_demo()
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
        print("\n\n데모 중단됨")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()