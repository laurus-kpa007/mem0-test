"""
텍스트 분류 서비스 - 메모리 자동 카테고리 분류
"""

import logging
from typing import Dict, List, Optional, Any
import ollama
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config.settings import load_config, AppConfig

logger = logging.getLogger(__name__)


class ClassificationService:
    """텍스트 자동 분류 서비스"""

    # 기본 카테고리 정의
    DEFAULT_CATEGORIES = {
        "personal_info": {
            "name": "개인정보",
            "keywords": ["이름", "나이", "생일", "주소", "연락처", "이메일", "직업", "학교"],
            "description": "개인 신상 정보"
        },
        "preferences": {
            "name": "선호도",
            "keywords": ["좋아", "싫어", "선호", "취향", "즐겨", "관심", "취미"],
            "description": "좋아하거나 싫어하는 것들"
        },
        "experiences": {
            "name": "경험",
            "keywords": ["여행", "경험", "추억", "사건", "일화", "갔", "했", "봤"],
            "description": "과거 경험이나 추억"
        },
        "knowledge": {
            "name": "지식",
            "keywords": ["알고", "배웠", "공부", "학습", "정보", "지식", "팁"],
            "description": "학습한 정보나 지식"
        },
        "relationships": {
            "name": "관계",
            "keywords": ["가족", "친구", "동료", "아는", "관계", "사람", "지인"],
            "description": "인간관계 정보"
        },
        "goals": {
            "name": "목표",
            "keywords": ["목표", "계획", "희망", "꿈", "하고싶", "될거", "예정"],
            "description": "목표나 계획"
        },
        "health": {
            "name": "건강",
            "keywords": ["건강", "운동", "식단", "질병", "아프", "병원", "약"],
            "description": "건강 관련 정보"
        },
        "work": {
            "name": "업무",
            "keywords": ["일", "업무", "회사", "프로젝트", "직장", "근무", "업무"],
            "description": "업무나 경력 관련"
        },
        "emotions": {
            "name": "감정",
            "keywords": ["기쁘", "슬프", "화나", "행복", "우울", "스트레스", "감정"],
            "description": "감정 상태"
        }
    }

    def __init__(self, config: Optional[AppConfig] = None):
        """
        분류 서비스 초기화

        Args:
            config: 애플리케이션 설정
        """
        self.config = config or load_config()
        self.categories = self.DEFAULT_CATEGORIES.copy()

    async def classify_text(
        self,
        text: str,
        custom_categories: Optional[Dict] = None
    ) -> str:
        """
        텍스트를 카테고리로 분류

        Args:
            text: 분류할 텍스트
            custom_categories: 커스텀 카테고리 (선택)

        Returns:
            str: 카테고리 키
        """
        try:
            categories_to_use = custom_categories or self.categories

            # 키워드 기반 빠른 분류 시도
            category = self._keyword_based_classification(text, categories_to_use)
            if category != "uncategorized":
                return category

            # LLM 기반 정밀 분류
            category = await self._llm_classification(text, categories_to_use)
            return category

        except Exception as e:
            logger.error(f"텍스트 분류 실패: {e}")
            return "uncategorized"

    def _keyword_based_classification(
        self,
        text: str,
        categories: Dict
    ) -> str:
        """
        키워드 기반 분류

        Args:
            text: 분류할 텍스트
            categories: 카테고리 정의

        Returns:
            str: 카테고리 키
        """
        text_lower = text.lower()
        scores = {}

        for cat_key, cat_info in categories.items():
            score = 0
            for keyword in cat_info["keywords"]:
                if keyword in text_lower:
                    score += 1
            scores[cat_key] = score

        # 가장 높은 점수의 카테고리
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                return best_category

        return "uncategorized"

    async def _llm_classification(
        self,
        text: str,
        categories: Dict
    ) -> str:
        """
        LLM을 사용한 정밀 분류

        Args:
            text: 분류할 텍스트
            categories: 카테고리 정의

        Returns:
            str: 카테고리 키
        """
        try:
            # 카테고리 설명 준비
            category_list = []
            for key, info in categories.items():
                category_list.append(f"{key}: {info['description']}")

            prompt = f"""다음 텍스트를 가장 적절한 카테고리로 분류하세요.

텍스트: "{text}"

카테고리:
{chr(10).join(category_list)}

가장 적절한 카테고리의 키(key)만 응답하세요. 적절한 카테고리가 없으면 'uncategorized'라고 응답하세요.

카테고리:"""

            response = ollama.generate(
                model=self.config.models.classification_model or self.config.models.chat_model,
                prompt=prompt,
                options={
                    "temperature": 0.1,  # 낮은 temperature로 일관성 향상
                    "num_predict": 20
                }
            )

            category = response['response'].strip().lower()

            # 유효성 검사
            if category in categories:
                return category

            return "uncategorized"

        except Exception as e:
            logger.error(f"LLM 분류 실패: {e}")
            return "uncategorized"

    async def extract_entities(
        self,
        text: str
    ) -> Dict[str, List[str]]:
        """
        텍스트에서 엔티티 추출

        Args:
            text: 분석할 텍스트

        Returns:
            Dict: 추출된 엔티티
        """
        try:
            prompt = f"""다음 텍스트에서 중요한 정보를 추출하세요.

텍스트: "{text}"

다음 정보를 JSON 형식으로 추출하세요:
- people: 사람 이름들
- places: 장소들
- dates: 날짜/시간
- organizations: 조직/회사
- keywords: 핵심 키워드

JSON:"""

            response = ollama.generate(
                model=self.config.models.chat_model,
                prompt=prompt,
                options={
                    "temperature": 0.1,
                    "num_predict": 256,
                    "format": "json"
                }
            )

            # JSON 파싱
            try:
                entities = json.loads(response['response'])
            except:
                entities = {
                    "people": [],
                    "places": [],
                    "dates": [],
                    "organizations": [],
                    "keywords": []
                }

            return entities

        except Exception as e:
            logger.error(f"엔티티 추출 실패: {e}")
            return {
                "people": [],
                "places": [],
                "dates": [],
                "organizations": [],
                "keywords": []
            }

    async def analyze_sentiment(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        감정 분석

        Args:
            text: 분석할 텍스트

        Returns:
            Dict: 감정 분석 결과
        """
        try:
            prompt = f"""다음 텍스트의 감정을 분석하세요.

텍스트: "{text}"

1. 감정 상태: positive/negative/neutral
2. 감정 강도: 1-5 (1=매우 약함, 5=매우 강함)
3. 주요 감정: 기쁨/슬픔/화남/두려움/놀람/혐오 중 선택

형식:
sentiment: [positive/negative/neutral]
intensity: [1-5]
emotion: [주요감정]"""

            response = ollama.generate(
                model=self.config.models.chat_model,
                prompt=prompt,
                options={
                    "temperature": 0.1,
                    "num_predict": 50
                }
            )

            # 응답 파싱
            result_text = response['response']
            lines = result_text.strip().split('\n')

            sentiment = "neutral"
            intensity = 3
            emotion = "neutral"

            for line in lines:
                if "sentiment:" in line:
                    sentiment = line.split(":")[-1].strip()
                elif "intensity:" in line:
                    try:
                        intensity = int(line.split(":")[-1].strip())
                    except:
                        intensity = 3
                elif "emotion:" in line:
                    emotion = line.split(":")[-1].strip()

            return {
                "sentiment": sentiment,
                "intensity": intensity,
                "emotion": emotion
            }

        except Exception as e:
            logger.error(f"감정 분석 실패: {e}")
            return {
                "sentiment": "neutral",
                "intensity": 3,
                "emotion": "neutral"
            }

    def add_custom_category(
        self,
        key: str,
        name: str,
        keywords: List[str],
        description: str
    ):
        """
        커스텀 카테고리 추가

        Args:
            key: 카테고리 키
            name: 카테고리 이름
            keywords: 키워드 목록
            description: 설명
        """
        self.categories[key] = {
            "name": name,
            "keywords": keywords,
            "description": description
        }
        logger.info(f"커스텀 카테고리 추가: {key}")

    def get_categories(self) -> Dict:
        """
        현재 카테고리 목록 반환

        Returns:
            Dict: 카테고리 정의
        """
        return self.categories.copy()