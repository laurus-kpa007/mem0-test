# 로컬 LLM 선택 가이드

## 1. 프로젝트 요구사항 분석

### 1.1 LLM이 수행해야 할 작업
- **대화 응답 생성**: 사용자와 자연스러운 대화
- **메모리 추출**: 대화에서 중요 정보 식별
- **텍스트 분류**: 메모리 카테고리 자동 분류
- **요약**: 긴 대화 내용 요약
- **임베딩 생성**: 벡터 검색용 임베딩
- **질문 이해**: 사용자 의도 파악

### 1.2 기술적 제약사항
- **하드웨어**: 일반 개인 PC/서버에서 실행 가능
- **응답 속도**: 3초 이내 응답
- **메모리 사용**: RAM 16GB 이내
- **GPU**: 선택적 (CPU로도 실행 가능)
- **한국어 지원**: 필수

## 2. 추천 LLM 모델

### 2.1 🥇 1순위: Qwen2.5 시리즈

#### Qwen2.5-7B-Instruct
```yaml
모델 크기: 7B 파라미터
메모리 요구: 4-6GB (4bit 양자화)
속도: 빠름 (RTX 3060에서 30-50 tokens/s)
한국어: 우수
특징:
  - 최신 모델 (2024년 릴리즈)
  - 뛰어난 한국어 이해력
  - 긴 컨텍스트 지원 (32K tokens)
  - 구조화된 출력 우수
```

#### Qwen2.5-14B-Instruct
```yaml
모델 크기: 14B 파라미터
메모리 요구: 8-10GB (4bit 양자화)
속도: 중간 (RTX 3060에서 20-30 tokens/s)
한국어: 매우 우수
특징:
  - 더 높은 정확도
  - 복잡한 추론 능력
  - 메모리 여유 있을 때 추천
```

### 2.2 🥈 2순위: Llama 3.2 시리즈

#### Llama-3.2-3B-Instruct
```yaml
모델 크기: 3B 파라미터
메모리 요구: 2-3GB
속도: 매우 빠름 (CPU에서도 실용적)
한국어: 보통
특징:
  - 가벼운 모델
  - 빠른 응답
  - 한국어는 추가 학습 필요
```

#### Llama-3.2-8B-Instruct
```yaml
모델 크기: 8B 파라미터
메모리 요구: 5-6GB (4bit 양자화)
속도: 빠름
한국어: 보통-양호
특징:
  - Meta의 최신 모델
  - 좋은 추론 능력
  - 커뮤니티 지원 활발
```

### 2.3 🥉 3순위: Mistral 시리즈

#### Mistral-7B-Instruct-v0.3
```yaml
모델 크기: 7B 파라미터
메모리 요구: 4-6GB (4bit 양자화)
속도: 빠름
한국어: 보통
특징:
  - 안정적인 성능
  - 효율적인 메모리 사용
  - 코드 이해 우수
```

### 2.4 특수 목적 모델

#### Solar-10.7B (Upstage)
```yaml
모델 크기: 10.7B 파라미터
메모리 요구: 6-8GB (4bit 양자화)
속도: 중간
한국어: 매우 우수
특징:
  - 한국 기업 개발
  - 한국어 특화
  - 깊은 병합(depth upscaling) 기술
```

#### EEVE-Korean-10.8B
```yaml
모델 크기: 10.8B 파라미터
메모리 요구: 6-8GB (4bit 양자화)
속도: 중간
한국어: 최우수
특징:
  - 한국어 전문
  - 한국 문화 이해
  - 맞춤법 검사 우수
```

## 3. 임베딩 모델

### 3.1 다국어 임베딩

#### BGE-M3
```yaml
크기: 568MB
차원: 1024
언어: 100+ 언어 지원
특징:
  - 한국어 우수
  - Dense + Sparse 검색
  - ColBERT 지원
```

#### Multilingual-E5-large
```yaml
크기: 1.1GB
차원: 1024
언어: 100+ 언어 지원
특징:
  - MS 개발
  - 높은 정확도
  - 긴 문서 지원
```

### 3.2 한국어 특화

#### KoSimCSE-RoBERTa
```yaml
크기: 440MB
차원: 768
특징:
  - 한국어 전용
  - 의미 유사도 우수
  - 빠른 속도
```

## 4. 구현 전략

### 4.1 하이브리드 접근법

```python
# 용도별 모델 분리
models = {
    "chat": "qwen2.5:7b",          # 대화용
    "classification": "qwen2.5:3b",  # 분류용 (빠른 모델)
    "embedding": "bge-m3",          # 임베딩용
    "summary": "qwen2.5:7b"         # 요약용
}
```

### 4.2 Ollama 설정

```bash
# Qwen2.5 설치 (추천)
ollama pull qwen2.5:7b
ollama pull qwen2.5:7b-instruct-q4_K_M  # 양자화 버전

# 대안 모델들
ollama pull llama3.2:8b
ollama pull mistral:7b-instruct
ollama pull solar:10.7b

# 임베딩 모델
ollama pull bge-m3
ollama pull nomic-embed-text
```

### 4.3 모델 최적화 설정

```yaml
# ollama 모델 설정
model_config:
  qwen2.5-7b:
    num_gpu: 1
    num_thread: 8
    num_ctx: 8192  # 컨텍스트 길이
    temperature: 0.7
    top_p: 0.9
    repeat_penalty: 1.1

  optimization:
    quantization: "q4_K_M"  # 4bit 양자화
    flash_attention: true    # Flash Attention 2
    kv_cache: true           # KV 캐시 활성화
```

## 5. 성능 비교표

| 모델 | 크기 | 메모리 | 속도 | 한국어 | 정확도 | 추천도 |
|------|------|--------|------|--------|---------|--------|
| Qwen2.5-7B | 7B | 4-6GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Qwen2.5-14B | 14B | 8-10GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Llama-3.2-3B | 3B | 2-3GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Llama-3.2-8B | 8B | 5-6GB | ⚡⚡⚡ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Mistral-7B | 7B | 4-6GB | ⚡⚡⚡ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Solar-10.7B | 10.7B | 6-8GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| EEVE-Korean | 10.8B | 6-8GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 6. 구현 예시

### 6.1 Ollama Python 클라이언트

```python
import ollama
from typing import List, Dict

class LocalLLMService:
    def __init__(self):
        self.chat_model = "qwen2.5:7b"
        self.embed_model = "bge-m3"

    async def chat(self, messages: List[Dict], context: str = None):
        """대화 생성"""
        if context:
            messages[0]["content"] = f"Context: {context}\n\n{messages[0]['content']}"

        response = await ollama.chat(
            model=self.chat_model,
            messages=messages,
            options={
                "temperature": 0.7,
                "num_ctx": 8192,
                "num_predict": 512
            }
        )
        return response['message']['content']

    async def extract_memory(self, text: str):
        """메모리 추출"""
        prompt = f"""다음 대화에서 기억해야 할 중요한 정보를 추출하세요.
        JSON 형식으로 응답하세요.

        대화: {text}

        형식:
        {{
            "facts": [],
            "preferences": [],
            "events": [],
            "relationships": []
        }}
        """

        response = await ollama.generate(
            model=self.chat_model,
            prompt=prompt,
            format="json"
        )
        return response['response']

    async def classify(self, text: str):
        """텍스트 분류"""
        categories = ["personal", "preference", "experience", "knowledge", "relationship", "goal", "health", "work"]

        prompt = f"""텍스트를 다음 카테고리 중 하나로 분류하세요: {categories}

        텍스트: {text}
        카테고리:"""

        response = await ollama.generate(
            model="qwen2.5:3b",  # 빠른 모델 사용
            prompt=prompt
        )
        return response['response'].strip()

    async def embed(self, text: str):
        """임베딩 생성"""
        response = await ollama.embeddings(
            model=self.embed_model,
            prompt=text
        )
        return response['embedding']
```

### 6.2 메모리 효율적 처리

```python
class OptimizedLLMService:
    def __init__(self):
        # 모델 풀 관리
        self.model_pool = {
            "heavy": "qwen2.5:7b",     # 복잡한 작업
            "light": "qwen2.5:3b",      # 간단한 작업
            "embed": "bge-m3"           # 임베딩
        }

    async def smart_process(self, task_type: str, input_text: str):
        """작업 유형에 따라 적절한 모델 선택"""

        # 텍스트 길이와 복잡도 평가
        complexity = self._assess_complexity(input_text)

        if task_type == "classification":
            model = self.model_pool["light"]
        elif complexity > 0.7:
            model = self.model_pool["heavy"]
        else:
            model = self.model_pool["light"]

        return await self._run_model(model, input_text)

    def _assess_complexity(self, text: str) -> float:
        """텍스트 복잡도 평가"""
        factors = {
            "length": len(text) / 1000,
            "entities": len(set(text.split())) / 100,
            "special_chars": len([c for c in text if not c.isalnum()]) / len(text)
        }
        return min(sum(factors.values()) / len(factors), 1.0)
```

## 7. 최종 추천

### 🎯 프로젝트에 최적화된 구성

```yaml
Primary Configuration:
  Chat Model: Qwen2.5-7B-Instruct (Q4_K_M)
  Classification Model: Qwen2.5-3B (Q4_K_M)
  Embedding Model: BGE-M3
  Fallback Model: Llama-3.2-3B

Hardware Requirements:
  Minimum:
    - RAM: 16GB
    - Storage: 20GB
    - GPU: Optional (GTX 1060 6GB+)

  Recommended:
    - RAM: 32GB
    - Storage: 50GB
    - GPU: RTX 3060 12GB or better

Performance Expectations:
  - Chat Response: 1-2 seconds
  - Classification: <500ms
  - Embedding: <100ms
  - Memory Search: <200ms
```

### 설치 스크립트

```bash
#!/bin/bash
# Ollama 설치 및 모델 다운로드

# Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 필수 모델 다운로드
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull qwen2.5:3b-q4_K_M
ollama pull bge-m3

# 선택적 모델
# ollama pull solar:10.7b  # 한국어 강화
# ollama pull llama3.2:3b  # 백업용

echo "모델 설치 완료!"
ollama list
```

## 8. 다음 단계

1. Ollama 설치 및 모델 다운로드
2. 성능 벤치마크 테스트
3. 한국어 처리 품질 평가
4. 파인튜닝 필요성 검토