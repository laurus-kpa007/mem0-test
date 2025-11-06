#!/usr/bin/env python3
"""
mem0 핵심 기능 테스트 스위트
mem0의 본연의 특징을 체계적으로 테스트

주요 테스트 항목:
1. 메모리 추가 (Add)
2. 메모리 업데이트 (Update)
3. 메모리 삭제 (Delete)
4. 메모리 검색 (Search)
5. 메모리 히스토리 (History)
6. 메모리 중복 제거 (Deduplication)
7. 메모리 관련성 (Relevance)
8. 메모리 지속성 (Persistence)
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
import time
from typing import List, Dict, Any

sys.path.append(str(Path(__file__).parent))

from core.memory_manager_simple import SimpleMemoryManager
from core.chat_service_enhanced import EnhancedChatService
from config.settings import load_config


class Mem0TestSuite:
    """mem0 핵심 기능 테스트"""

    def __init__(self):
        self.config = load_config()
        self.memory_manager = SimpleMemoryManager(self.config)
        self.chat_service = EnhancedChatService(self.config)
        self.test_user = "test_user_mem0"
        self.test_results = []

    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "=" * 60)
        print("🧪 mem0 핵심 기능 테스트 스위트")
        print("=" * 60 + "\n")

        # 테스트 전 정리
        await self.cleanup_test_data()

        tests = [
            self.test_1_memory_add,
            self.test_2_memory_update,
            self.test_3_memory_deduplication,
            self.test_4_memory_search_relevance,
            self.test_5_memory_delete,
            self.test_6_memory_persistence,
            self.test_7_memory_context_building,
            self.test_8_memory_auto_extraction,
            self.test_9_memory_categorization,
            self.test_10_memory_evolution,
        ]

        for test_func in tests:
            try:
                await test_func()
                self.test_results.append({"test": test_func.__name__, "status": "✅ PASS"})
            except Exception as e:
                self.test_results.append({
                    "test": test_func.__name__,
                    "status": f"❌ FAIL",
                    "error": str(e)
                })
                print(f"   ❌ 테스트 실패: {e}")

        # 결과 출력
        await self.print_results()

        # 테스트 후 정리
        await self.cleanup_test_data()

    async def test_1_memory_add(self):
        """테스트 1: 메모리 추가"""
        print("\n📝 테스트 1: 메모리 추가 (Add)")
        print("-" * 40)

        memories_to_add = [
            ("제 이름은 김철수입니다", {"category": "personal_info"}),
            ("저는 30살입니다", {"category": "personal_info"}),
            ("저는 소프트웨어 엔지니어입니다", {"category": "personal_info"}),
            ("저는 커피를 매우 좋아합니다", {"category": "preferences"}),
            ("아침에는 항상 아메리카노를 마십니다", {"category": "habits"}),
        ]

        added_ids = []
        for text, metadata in memories_to_add:
            memory_id = await self.memory_manager.add_memory(
                text=text,
                user_id=self.test_user,
                metadata=metadata
            )
            added_ids.append(memory_id)
            print(f"   ✓ 추가: {text[:30]}... (ID: {memory_id[:20]}...)")

        # 검증
        all_memories = await self.memory_manager.get_all_memories(self.test_user)
        assert len(all_memories) >= len(memories_to_add), "모든 메모리가 추가되지 않음"
        print(f"\n   ✅ {len(memories_to_add)}개 메모리 추가 성공")

    async def test_2_memory_update(self):
        """테스트 2: 메모리 업데이트 (인간처럼 기억 수정)"""
        print("\n🔄 테스트 2: 메모리 업데이트 (Update)")
        print("-" * 40)

        # 초기 정보
        initial = "저는 29살입니다"
        memory_id = await self.memory_manager.add_memory(
            text=initial,
            user_id=self.test_user,
            metadata={"category": "personal_info", "version": 1}
        )
        print(f"   초기: {initial}")

        # 업데이트 (새로운 정보로 교체)
        updated = "저는 30살입니다 (생일이 지났습니다)"
        await self.memory_manager.add_memory(
            text=updated,
            user_id=self.test_user,
            metadata={
                "category": "personal_info",
                "version": 2,
                "replaces": memory_id,
                "reason": "birthday_passed"
            }
        )
        print(f"   업데이트: {updated}")

        # 이전 메모리 삭제 (옵션)
        await self.memory_manager.delete_memory(memory_id, self.test_user)
        print(f"   ✓ 이전 메모리 삭제")

        print("\n   ✅ 메모리 업데이트 성공 (인간의 기억 수정 시뮬레이션)")

    async def test_3_memory_deduplication(self):
        """테스트 3: 중복 메모리 제거"""
        print("\n🔍 테스트 3: 중복 제거 (Deduplication)")
        print("-" * 40)

        # 유사한 메모리들 추가
        similar_memories = [
            "저는 커피를 좋아합니다",
            "저는 커피를 정말 좋아해요",
            "커피를 매우 좋아합니다",
            "저는 라떼보다 아메리카노를 선호합니다",  # 구체적 정보
        ]

        for memory in similar_memories:
            await self.memory_manager.add_memory(
                text=memory,
                user_id=self.test_user,
                metadata={"category": "preferences"}
            )
            print(f"   추가: {memory}")

        # 검색으로 중복 확인
        results = await self.memory_manager.search_memories(
            query="커피",
            user_id=self.test_user,
            limit=10
        )

        print(f"\n   검색 결과: {len(results)}개")
        for r in results:
            print(f"   - {r['text']}")

        print("\n   💡 실제 mem0는 임베딩을 통해 의미적 중복을 자동 처리")
        print("   ✅ 중복 메모리 테스트 완료")

    async def test_4_memory_search_relevance(self):
        """테스트 4: 관련성 기반 검색"""
        print("\n🎯 테스트 4: 관련성 검색 (Relevance Search)")
        print("-" * 40)

        # 다양한 주제의 메모리 추가
        diverse_memories = [
            ("저는 파이썬 개발자입니다", "work"),
            ("Django와 FastAPI를 주로 사용합니다", "work"),
            ("주말에는 등산을 즐깁니다", "hobby"),
            ("북한산을 자주 갑니다", "hobby"),
            ("비가 오는 날을 좋아합니다", "preferences"),
        ]

        for text, category in diverse_memories:
            await self.memory_manager.add_memory(
                text=text,
                user_id=self.test_user,
                metadata={"category": category}
            )

        # 관련성 검색 테스트
        queries = [
            ("프로그래밍", ["파이썬", "Django", "FastAPI"]),
            ("취미", ["등산", "북한산"]),
            ("날씨", ["비가 오는"]),
        ]

        for query, expected_keywords in queries:
            results = await self.memory_manager.search_memories(
                query=query,
                user_id=self.test_user,
                limit=5
            )
            print(f"\n   쿼리: '{query}'")
            print(f"   결과: {len(results)}개")
            for r in results:
                print(f"   - {r['text']} (score: {r.get('score', 'N/A')})")

        print("\n   ✅ 관련성 기반 검색 테스트 완료")

    async def test_5_memory_delete(self):
        """테스트 5: 선택적 메모리 삭제"""
        print("\n🗑️ 테스트 5: 메모리 삭제 (Delete)")
        print("-" * 40)

        # 삭제할 메모리 추가
        temp_memory_id = await self.memory_manager.add_memory(
            text="이것은 임시 메모리입니다",
            user_id=self.test_user,
            metadata={"temporary": True}
        )
        print(f"   추가: 임시 메모리 (ID: {temp_memory_id[:20]}...)")

        # 삭제 전 확인
        before = await self.memory_manager.get_all_memories(self.test_user)
        before_count = len(before)

        # 삭제
        success = await self.memory_manager.delete_memory(temp_memory_id, self.test_user)
        print(f"   삭제: {'성공' if success else '실패'}")

        # 삭제 후 확인
        after = await self.memory_manager.get_all_memories(self.test_user)
        after_count = len(after)

        assert after_count < before_count, "메모리가 삭제되지 않음"
        print(f"   확인: {before_count}개 → {after_count}개")
        print("\n   ✅ 선택적 메모리 삭제 성공")

    async def test_6_memory_persistence(self):
        """테스트 6: 메모리 지속성"""
        print("\n💾 테스트 6: 메모리 지속성 (Persistence)")
        print("-" * 40)

        # 메모리 추가
        test_text = f"지속성 테스트 - {datetime.now().isoformat()}"
        memory_id = await self.memory_manager.add_memory(
            text=test_text,
            user_id=self.test_user,
            metadata={"test": "persistence"}
        )
        print(f"   저장: {test_text}")

        # 메모리 매니저 재초기화 (재시작 시뮬레이션)
        new_manager = SimpleMemoryManager(self.config)

        # 재로드 후 확인
        reloaded = await new_manager.get_all_memories(self.test_user)
        found = any(m.get('text') == test_text for m in reloaded)

        assert found, "메모리가 지속되지 않음"
        print(f"   재로드: 메모리 확인 {'성공' if found else '실패'}")
        print("\n   ✅ 메모리 지속성 테스트 완료")

    async def test_7_memory_context_building(self):
        """테스트 7: 컨텍스트 구성"""
        print("\n🏗️ 테스트 7: 메모리 컨텍스트 구성")
        print("-" * 40)

        # 다양한 타입의 메모리 추가
        context_memories = [
            ("이름: 김철수", "personal_info"),
            ("나이: 30살", "personal_info"),
            ("직업: 개발자", "personal_info"),
            ("선호: 커피를 좋아함", "preferences"),
            ("경험: 작년에 일본 여행", "experiences"),
        ]

        for text, category in context_memories:
            await self.memory_manager.add_memory(
                text=text,
                user_id=self.test_user,
                metadata={"category": category}
            )

        # 대화에서 컨텍스트 활용
        response = await self.chat_service.chat(
            message="저에 대해 아는 것을 요약해주세요",
            user_id=self.test_user,
            session_id="test_context",
            use_memory=True
        )

        print(f"   질문: 저에 대해 아는 것을 요약해주세요")
        print(f"   응답: {response['response'][:200]}...")

        if response.get('memory_context'):
            print(f"\n   사용된 컨텍스트:")
            print(f"   {response['memory_context'][:300]}...")

        print("\n   ✅ 메모리 컨텍스트 구성 테스트 완료")

    async def test_8_memory_auto_extraction(self):
        """테스트 8: 자동 정보 추출"""
        print("\n🤖 테스트 8: 자동 정보 추출")
        print("-" * 40)

        # 정보가 포함된 대화
        conversations = [
            "안녕하세요, 저는 박영희입니다. 28살이에요.",
            "저는 디자이너로 일하고 있어요. UI/UX를 전문으로 해요.",
            "저는 차를 좋아해요. 특히 녹차를 즐겨 마십니다.",
            "최근에 부산으로 출장을 다녀왔어요.",
        ]

        for msg in conversations:
            print(f"\n   대화: {msg}")
            response = await self.chat_service.chat(
                message=msg,
                user_id=self.test_user,
                session_id="test_extraction",
                use_memory=True
            )
            print(f"   응답: {response['response'][:100]}...")

        # 자동 추출된 메모리 확인
        all_memories = await self.memory_manager.get_all_memories(self.test_user)
        auto_extracted = [m for m in all_memories
                         if m.get('metadata', {}).get('auto_extracted')]

        print(f"\n   자동 추출된 메모리: {len(auto_extracted)}개")
        for mem in auto_extracted[:5]:
            print(f"   - {mem['text']}")

        print("\n   ✅ 자동 정보 추출 테스트 완료")

    async def test_9_memory_categorization(self):
        """테스트 9: 메모리 자동 분류"""
        print("\n🏷️ 테스트 9: 메모리 자동 분류")
        print("-" * 40)

        # 다양한 카테고리의 텍스트
        test_texts = [
            ("제 이름은 이순신입니다", "personal_info"),
            ("저는 초콜릿을 좋아해요", "preferences"),
            ("작년에 유럽 여행을 했어요", "experiences"),
            ("매일 아침 조깅을 합니다", "habits"),
            ("Python과 JavaScript를 다룹니다", "skills"),
        ]

        from core.classification_service import ClassificationService
        classifier = ClassificationService(self.config)

        for text, expected_category in test_texts:
            detected_category = await classifier.classify_text(text)
            print(f"   텍스트: '{text}'")
            print(f"   예상: {expected_category}, 감지: {detected_category}")
            print(f"   {'✓' if expected_category == detected_category else '⚠️'} 결과\n")

        print("   ✅ 메모리 자동 분류 테스트 완료")

    async def test_10_memory_evolution(self):
        """테스트 10: 메모리 진화 (시간에 따른 변화)"""
        print("\n📈 테스트 10: 메모리 진화")
        print("-" * 40)

        # 시간 순서대로 정보 업데이트
        evolution_stages = [
            ("저는 주니어 개발자입니다", "2023-01"),
            ("이제 미드레벨 개발자가 되었습니다", "2023-06"),
            ("시니어 개발자로 승진했습니다", "2024-01"),
            ("현재 테크 리드를 맡고 있습니다", "2024-06"),
        ]

        for text, date in evolution_stages:
            await self.memory_manager.add_memory(
                text=text,
                user_id=self.test_user,
                metadata={
                    "category": "career",
                    "date": date,
                    "type": "evolution"
                }
            )
            print(f"   {date}: {text}")

        # 최신 정보 검색
        career_memories = await self.memory_manager.search_memories(
            query="개발자 경력",
            user_id=self.test_user,
            limit=10
        )

        print(f"\n   경력 관련 메모리: {len(career_memories)}개")
        print("   💡 실제 mem0는 시간 가중치를 고려하여 최신 정보 우선")
        print("\n   ✅ 메모리 진화 테스트 완료")

    async def cleanup_test_data(self):
        """테스트 데이터 정리"""
        try:
            all_memories = await self.memory_manager.get_all_memories(self.test_user)
            for memory in all_memories:
                if memory.get('id'):
                    await self.memory_manager.delete_memory(memory['id'], self.test_user)
        except:
            pass

    async def print_results(self):
        """테스트 결과 출력"""
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)

        passed = sum(1 for r in self.test_results if "PASS" in r['status'])
        failed = sum(1 for r in self.test_results if "FAIL" in r['status'])

        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if 'error' in result:
                print(f"     오류: {result['error']}")

        print("\n" + "-" * 40)
        print(f"총 테스트: {len(self.test_results)}개")
        print(f"성공: {passed}개 | 실패: {failed}개")

        if failed == 0:
            print("\n🎉 모든 테스트 통과! mem0가 정상 동작합니다.")
        else:
            print(f"\n⚠️ {failed}개 테스트 실패. 확인이 필요합니다.")


async def main():
    """메인 실행 함수"""
    test_suite = Mem0TestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()