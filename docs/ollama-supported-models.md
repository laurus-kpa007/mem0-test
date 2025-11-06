# Ollama 공식 지원 모델 리스트

## 1. ✅ Ollama 공식 지원 모델 (2024년 11월 기준)

### 1.1 대화형 모델 (Chat Models)

#### ✅ **Qwen 시리즈** (Alibaba)
```bash
# 공식 지원
ollama pull qwen2.5:0.5b   # 0.5B 파라미터
ollama pull qwen2.5:1.5b   # 1.5B 파라미터
ollama pull qwen2.5:3b     # 3B 파라미터
ollama pull qwen2.5:7b     # 7B 파라미터 ⭐ 추천
ollama pull qwen2.5:14b    # 14B 파라미터
ollama pull qwen2.5:32b    # 32B 파라미터
ollama pull qwen2.5:72b    # 72B 파라미터

# Coder 버전 (코드 특화)
ollama pull qwen2.5-coder:7b
```

#### ✅ **Llama 시리즈** (Meta)
```bash
# Llama 3.2
ollama pull llama3.2:1b    # 1B 파라미터
ollama pull llama3.2:3b    # 3B 파라미터 ⭐ 추천
ollama pull llama3.2:8b    # 8B 파라미터

# Llama 3.1
ollama pull llama3.1:8b
ollama pull llama3.1:70b
ollama pull llama3.1:405b
```

#### ✅ **Mistral 시리즈**
```bash
ollama pull mistral:7b          # Mistral 7B
ollama pull mistral-nemo:12b    # Mistral Nemo 12B
ollama pull mistral-small:22b   # Mistral Small 22B
```

#### ✅ **Gemma 시리즈** (Google)
```bash
ollama pull gemma2:2b
ollama pull gemma2:9b
ollama pull gemma2:27b
```

#### ✅ **Phi 시리즈** (Microsoft)
```bash
ollama pull phi3:3.8b
ollama pull phi3:14b
ollama pull phi3.5:3.8b
```

### 1.2 임베딩 모델 (Embedding Models)

#### ✅ **공식 지원 임베딩 모델**
```bash
ollama pull nomic-embed-text    # Nomic AI 임베딩 (137M)
ollama pull mxbai-embed-large   # MixedBread AI (335M)
ollama pull all-minilm          # Sentence Transformers (23M)
ollama pull bge-small           # BAAI BGE Small (33M)
ollama pull bge-base            # BAAI BGE Base (109M)
ollama pull bge-large           # BAAI BGE Large (335M)
```

#### ⚠️ **BGE-M3는 직접 변환 필요**
```bash
# BGE-M3는 Ollama 공식 지원 X
# 하지만 커스텀 모델로 추가 가능 (아래 참조)
```

### 1.3 한국어 특화 모델

#### ⚠️ **부분 지원 또는 커뮤니티 모델**
```bash
# Solar - 커뮤니티 버전 존재
ollama pull solar:10.7b  # 확인 필요

# EEVE-Korean - 공식 지원 X
# 커스텀 모델로 추가 필요

# Polyglot-Ko - 공식 지원 X
# 커스텀 모델로 추가 필요
```

## 2. 🔧 커스텀 모델 추가 방법

### 2.1 GGUF 파일로 커스텀 모델 생성

```bash
# 1. GGUF 파일 다운로드 (Hugging Face에서)
wget https://huggingface.co/username/model/resolve/main/model.gguf

# 2. Modelfile 생성
cat > Modelfile << EOF
FROM ./model.gguf

TEMPLATE """{{ .Prompt }}"""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "</s>"
EOF

# 3. Ollama 모델 생성
ollama create mymodel -f Modelfile

# 4. 실행
ollama run mymodel
```

### 2.2 BGE-M3 커스텀 추가 예시

```bash
# BGE-M3를 Ollama에 추가하는 방법
cat > Modelfile-bge-m3 << 'EOF'
FROM ./bge-m3.gguf

TEMPLATE """{{ .Prompt }}"""

PARAMETER embedding_only true
PARAMETER pooling_type mean
EOF

ollama create bge-m3 -f Modelfile-bge-m3
```

## 3. 📊 프로젝트용 실제 사용 가능 모델

### 3.1 ✅ **즉시 사용 가능 (공식 지원)**

```yaml
대화 모델:
  - qwen2.5:7b ⭐⭐⭐⭐⭐ (최고 추천)
  - qwen2.5:3b ⭐⭐⭐⭐ (경량)
  - llama3.2:3b ⭐⭐⭐ (백업)
  - llama3.2:8b ⭐⭐⭐
  - mistral:7b ⭐⭐
  - gemma2:9b ⭐⭐⭐
  - phi3.5:3.8b ⭐⭐ (경량)

임베딩 모델:
  - nomic-embed-text ⭐⭐⭐⭐ (추천)
  - mxbai-embed-large ⭐⭐⭐⭐ (대안)
  - bge-large ⭐⭐⭐
  - all-minilm ⭐⭐ (경량)
```

### 3.2 ⚠️ **추가 작업 필요**

```yaml
커스텀 변환 필요:
  - BGE-M3 (GGUF 변환 필요)
  - Solar-10.7B (커뮤니티 버전 확인)
  - EEVE-Korean (GGUF 변환 필요)
```

## 4. 🎯 수정된 최종 추천

### 4.1 **메인 구성 (모두 Ollama 공식 지원)**

```python
# config.py
OLLAMA_MODELS = {
    "chat": "qwen2.5:7b",           # 메인 대화 (공식 지원) ✅
    "light": "qwen2.5:3b",           # 경량 작업 (공식 지원) ✅
    "embedding": "nomic-embed-text",  # 임베딩 (공식 지원) ✅
    "fallback": "llama3.2:3b"        # 백업 (공식 지원) ✅
}

# 설치 스크립트
install_models.sh:
"""
#!/bin/bash
# 모든 모델 Ollama 공식 지원

ollama pull qwen2.5:7b
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
ollama pull llama3.2:3b

echo "✅ 모든 모델 설치 완료"
ollama list
"""
```

### 4.2 **대안 구성 (한국어 중심)**

```python
# 한국어 최적화 구성
OLLAMA_MODELS_KR = {
    "chat": "qwen2.5:14b",           # 더 큰 모델로 한국어 성능 향상 ✅
    "light": "gemma2:2b",            # Google 경량 모델 ✅
    "embedding": "mxbai-embed-large", # 다국어 임베딩 ✅
    "fallback": "phi3.5:3.8b"        # MS 경량 모델 ✅
}
```

## 5. 📝 모델별 메모리 요구사항

| 모델 | 양자화 | VRAM/RAM | 공식 지원 |
|------|--------|----------|-----------|
| qwen2.5:7b | Q4_K_M | 4-5GB | ✅ |
| qwen2.5:3b | Q4_K_M | 2-3GB | ✅ |
| qwen2.5:14b | Q4_K_M | 8-9GB | ✅ |
| llama3.2:3b | Q4_K_M | 2-3GB | ✅ |
| llama3.2:8b | Q4_K_M | 5-6GB | ✅ |
| mistral:7b | Q4_K_M | 4-5GB | ✅ |
| gemma2:9b | Q4_K_M | 5-6GB | ✅ |
| nomic-embed-text | F16 | 274MB | ✅ |
| mxbai-embed-large | F16 | 670MB | ✅ |

## 6. 🚀 빠른 시작 가이드

```bash
# 1. Ollama 설치 (Windows)
# https://ollama.com/download/windows 에서 다운로드

# 2. 필수 모델 설치 (모두 공식 지원)
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# 3. 테스트
ollama run qwen2.5:7b "안녕하세요, 한국어 테스트입니다."

# 4. Python에서 사용
pip install ollama

python -c "
import ollama
response = ollama.chat(model='qwen2.5:7b', messages=[
    {'role': 'user', 'content': '안녕하세요!'}
])
print(response['message']['content'])
"
```

## 7. ⚠️ 주의사항

### 공식 지원 모델 확인 방법
```bash
# Ollama에서 사용 가능한 모델 리스트
ollama list

# Ollama 라이브러리에서 검색
ollama search qwen
ollama search llama
ollama search embed
```

### 모델 업데이트
```bash
# 최신 버전으로 업데이트
ollama pull qwen2.5:7b

# 특정 버전 고정
ollama pull qwen2.5:7b-q4_K_M
```

## 8. 결론

✅ **프로젝트에 사용할 모델 (모두 Ollama 공식 지원)**:
- **대화**: `qwen2.5:7b` (한국어 우수, 공식 지원)
- **분류**: `qwen2.5:3b` (빠른 처리, 공식 지원)
- **임베딩**: `nomic-embed-text` (효율적, 공식 지원)
- **백업**: `llama3.2:3b` (경량, 공식 지원)

이 구성은 모두 Ollama에서 공식 지원하므로 별도의 변환 작업 없이 바로 사용 가능합니다!