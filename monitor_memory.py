#!/usr/bin/env python3
"""
실시간 메모리 모니터링 도구
메모리 변화를 실시간으로 관찰합니다
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
import os

init()

class MemoryMonitor:
    def __init__(self):
        self.data_dir = Path("data")
        self.memories_file = self.data_dir / "local_memories.json"
        self.last_state = {}
        self.last_modified = 0

    def read_memories(self):
        """메모리 파일 읽기"""
        if not self.memories_file.exists():
            return {}

        try:
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def display_changes(self, old_state, new_state):
        """변경사항 표시"""
        # 새로운 사용자 확인
        for user_id in new_state:
            if user_id not in old_state:
                print(Fore.GREEN + f"\n🆕 새 사용자: {user_id}" + Style.RESET_ALL)
                for memory in new_state[user_id]:
                    self.display_memory(memory, is_new=True)

        # 기존 사용자의 새 메모리 확인
        for user_id in new_state:
            if user_id in old_state:
                old_memories = old_state[user_id]
                new_memories = new_state[user_id]

                # ID 목록 비교
                old_ids = {m.get('id') for m in old_memories}
                new_ids = {m.get('id') for m in new_memories}

                # 새로 추가된 메모리
                added_ids = new_ids - old_ids
                if added_ids:
                    print(Fore.CYAN + f"\n👤 사용자 {user_id}에 새 메모리 추가:" + Style.RESET_ALL)
                    for memory in new_memories:
                        if memory.get('id') in added_ids:
                            self.display_memory(memory, is_new=True)

                # 삭제된 메모리
                deleted_ids = old_ids - new_ids
                if deleted_ids:
                    print(Fore.RED + f"\n🗑️ 사용자 {user_id}에서 메모리 삭제: {len(deleted_ids)}개" + Style.RESET_ALL)

    def display_memory(self, memory, is_new=False):
        """메모리 표시"""
        icon = "✨" if is_new else "📝"
        print(f"\n   {icon} {memory.get('text', 'N/A')}")
        metadata = memory.get('metadata', {})
        if metadata:
            print(f"      카테고리: {metadata.get('category', 'N/A')}")
            print(f"      시간: {metadata.get('timestamp', 'N/A')}")
            if metadata.get('auto_extracted'):
                print(f"      🤖 자동 추출됨")

    def display_summary(self, state):
        """요약 정보 표시"""
        total_users = len(state)
        total_memories = sum(len(memories) for memories in state.values())

        # 화면 지우기 (Windows)
        os.system('cls' if os.name == 'nt' else 'clear')

        print(Fore.CYAN + "=" * 60)
        print("🔍 메모리 실시간 모니터링")
        print("=" * 60 + Style.RESET_ALL)
        print(f"\n📊 현재 상태:")
        print(f"   사용자 수: {total_users}")
        print(f"   총 메모리: {total_memories}개")
        print(f"\n⏰ 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "-" * 60)

        # 사용자별 요약
        if state:
            print("\n👥 사용자별 메모리:")
            for user_id, memories in state.items():
                print(f"   • {user_id}: {len(memories)}개")

                # 최근 메모리 1개만 표시
                if memories:
                    latest = memories[-1]
                    print(f"     최근: {latest.get('text', 'N/A')[:50]}...")

    def monitor(self, interval=2):
        """실시간 모니터링"""
        print(Fore.YELLOW + "메모리 모니터링을 시작합니다... (종료: Ctrl+C)" + Style.RESET_ALL)
        print("파일 변경을 감지하면 자동으로 표시됩니다.\n")

        try:
            while True:
                # 파일 변경 확인
                if self.memories_file.exists():
                    current_modified = self.memories_file.stat().st_mtime

                    if current_modified != self.last_modified:
                        # 변경 감지
                        new_state = self.read_memories()

                        if self.last_state:
                            # 변경사항 표시
                            self.display_changes(self.last_state, new_state)

                        # 요약 표시
                        self.display_summary(new_state)

                        self.last_state = new_state
                        self.last_modified = current_modified

                        print(Fore.GREEN + "\n✅ 업데이트 감지!" + Style.RESET_ALL)

                time.sleep(interval)

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\n모니터링 종료" + Style.RESET_ALL)
            self.show_final_summary()

    def show_final_summary(self):
        """최종 요약"""
        state = self.read_memories()
        if state:
            print("\n" + "=" * 60)
            print("📊 최종 요약")
            print("=" * 60)

            for user_id, memories in state.items():
                print(f"\n👤 {user_id}")
                print(f"   총 {len(memories)}개 메모리")

                # 카테고리별 집계
                categories = {}
                for memory in memories:
                    cat = memory.get('metadata', {}).get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1

                if categories:
                    print("   카테고리:")
                    for cat, count in categories.items():
                        print(f"   - {cat}: {count}개")


def main():
    """메인 함수"""
    monitor = MemoryMonitor()

    print(Fore.CYAN + "\n메모리 모니터링 도구" + Style.RESET_ALL)
    print("=" * 40)
    print("1. 실시간 모니터링 (파일 변경 감지)")
    print("2. 현재 상태만 확인")

    choice = input("\n선택 (1 또는 2): ")

    if choice == "1":
        monitor.monitor()
    elif choice == "2":
        state = monitor.read_memories()
        monitor.display_summary(state)

        if state:
            print("\n상세 내용을 보시겠습니까? (y/n): ", end="")
            if input().lower() == 'y':
                for user_id, memories in state.items():
                    print(f"\n{'=' * 40}")
                    print(f"👤 사용자: {user_id}")
                    print(f"{'=' * 40}")

                    for i, memory in enumerate(memories, 1):
                        print(f"\n[{i}] {memory.get('text', 'N/A')}")
                        metadata = memory.get('metadata', {})
                        if metadata:
                            print(f"    카테고리: {metadata.get('category', 'N/A')}")
                            print(f"    시간: {metadata.get('timestamp', 'N/A')}")
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()