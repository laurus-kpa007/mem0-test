# mem0 LTM 프로젝트 설정 가이드

## 📋 목차
1. [사전 요구사항](#사전-요구사항)
2. [빠른 시작](#빠른-시작)
3. [상세 설정](#상세-설정)
4. [모델 관리](#모델-관리)
5. [문제 해결](#문제-해결)

## 🚀 사전 요구사항

### 시스템 요구사항
- **OS**: Windows 10/11, macOS, Linux
- **Python**: 3.9 이상
- **RAM**: 최소 16GB (권장 32GB)
- **Storage**: 최소 20GB 여유 공간
- **GPU**: 선택사항 (NVIDIA GPU 권장)

### 필수 소프트웨어
1. **Python 3.9+**
2. **Ollama**
3. **Git**
4. **Docker** (선택사항)

## ⚡ 빠른 시작

### 1단계: 프로젝트 클론 및 환경 설정

```bash
# 프로젝트 클론
git clone https://github.com/your-username/mem0-test.git
cd mem0-test

# 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2단계: Ollama 설치

#### Windows
```bash
# Ollama 다운로드 및 설치
# https://ollama.com/download/windows 에서 설치 파일 다운로드
```

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 3단계: Ollama 서비스 시작

```bash
# Ollama 서비스 시작
ollama serve

# 새 터미널에서 모델 설정 스크립트 실행
python setup_models.py
```

### 4단계: 모델 자동 설정

```bash
# 모델 자동 감지 및 설정
python setup_models.py

# 옵션 선택:
# 1. 빠른 설치 (필수 모델만) - 추천
# 2. 대화형 설치 (추천 모델 선택)
# 3. 검증만 수행
```

## 🔧 상세 설정

### 설정 파일 구조

프로젝트는 자동으로 Ollama에 설치된 모델을 감지하고 설정합니다.

#### `config/settings.py` 주요 클래스

```python
# 모델 설정
ModelConfig:
  - chat_model: 대화용 모델 (자동 감지)
  - classification_model: 분류용 모델 (자동 감지)
  - embedding_model: 임베딩 모델 (nomic-embed-text)
  - summary_model: 요약용 모델
  - fallback_model: 백업 모델

# 데이터베이스 설정
DatabaseConfig:
  - vector_db_type: "qdrant" (벡터 DB)
  - metadata_db_type: "sqlite" (메타데이터)
  - redis 캐시 (선택사항)

# 메모리 설정
MemoryConfig:
  - max_short_term_memories: 100
  - max_long_term_memories: 10000
  - similarity_threshold: 0.7
```

### OllamaManager 기능

```python
from config.settings import OllamaManager, initialize_config

# Ollama 모델 관리자 초기화
ollama = OllamaManager()

# 설치된 모델 목록 확인
models = ollama.list_models()
for model in models:
    print(f"{model.name} ({model.size})")

# 특정 모델 설치 확인
if ollama.is_model_available("qwen2.5:7b"):
    print("모델이 설치되어 있습니다")

# 모델 다운로드
ollama.pull_model("qwen2.5:7b")

# 자동 모델 선택
config = initialize_config()  # 자동으로 최적 모델 선택
```

## 📦 모델 관리

### 추천 모델 우선순위

#### 대화 모델 (Chat)
1. **qwen2.5:7b** ⭐⭐⭐⭐⭐ - 최고 추천
2. **qwen2.5:14b** ⭐⭐⭐⭐ - 고성능
3. **llama3.2:8b** ⭐⭐⭐ - 대안
4. **mistral:7b** ⭐⭐ - 경량

#### 분류 모델 (Classification)
1. **qwen2.5:3b** ⭐⭐⭐⭐⭐ - 빠른 처리
2. **llama3.2:3b** ⭐⭐⭐ - 대안
3. **phi3:3.8b** ⭐⭐⭐ - MS 모델

#### 임베딩 모델 (Embedding)
1. **nomic-embed-text** ⭐⭐⭐⭐⭐ - 추천
2. **mxbai-embed-large** ⭐⭐⭐⭐ - 대안
3. **bge-large** ⭐⭐⭐ - BAAI

### 모델 수동 설치

```bash
# 필수 모델 설치
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# 선택 모델 설치
ollama pull qwen2.5:3b  # 분류용
ollama pull llama3.2:3b  # 백업용

# 설치 확인
ollama list
```

### 모델 설정 커스터마이징

```python
# config/config.json 직접 편집
{
  "models": {
    "chat_model": "qwen2.5:7b",
    "classification_model": "qwen2.5:3b",
    "embedding_model": "nomic-embed-text",
    "model_params": {
      "chat": {
        "temperature": 0.7,
        "num_ctx": 8192,
        "num_predict": 1024
      }
    }
  }
}
```

## 🐳 Docker 설정 (선택사항)

### Qdrant 벡터 DB 실행

```bash
# Qdrant 실행
docker run -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Redis 캐시 실행 (선택사항)
docker run -d -p 6379:6379 redis:alpine
```

### Docker Compose 사용

```yaml
# docker-compose.yml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

```bash
docker-compose up -d
```

## 🧪 설정 검증

### 1. Python 환경 확인

```bash
python -c "import sys; print(f'Python {sys.version}')"
python -c "import ollama; print('Ollama 패키지 OK')"
python -c "import mem0; print('mem0 패키지 OK')"
```

### 2. Ollama 연결 테스트

```python
# test_ollama.py
import ollama

# Ollama 연결 테스트
try:
    response = ollama.list()
    print("✅ Ollama 연결 성공")
    print(f"설치된 모델: {[m['name'] for m in response['models']]}")
except Exception as e:
    print(f"❌ Ollama 연결 실패: {e}")
```

### 3. 전체 시스템 테스트

```python
# test_system.py
from config.settings import initialize_config

# 설정 초기화 및 검증
config = initialize_config()

print("=== 시스템 설정 ===")
print(f"대화 모델: {config.models.chat_model}")
print(f"임베딩 모델: {config.models.embedding_model}")
print(f"데이터 디렉토리: {config.data_dir}")
print("\n✅ 시스템 준비 완료!")
```

## ❗ 문제 해결

### Ollama 관련 문제

#### "Ollama가 설치되어 있지 않습니다"
```bash
# 설치 확인
ollama --version

# 재설치 필요시 공식 사이트에서 다운로드
# https://ollama.com/download
```

#### "Ollama 서비스에 연결할 수 없습니다"
```bash
# 서비스 시작
ollama serve

# 포트 확인 (기본 11434)
netstat -an | grep 11434
```

#### "모델을 찾을 수 없습니다"
```bash
# 모델 재설치
ollama pull qwen2.5:7b

# 모델 목록 확인
ollama list
```

### Python 패키지 문제

#### "ModuleNotFoundError"
```bash
# 가상환경 활성화 확인
which python  # Mac/Linux
where python  # Windows

# 패키지 재설치
pip install -r requirements.txt
```

### 메모리 부족 문제

#### GPU 메모리 부족
```python
# 더 작은 모델 사용
config.models.chat_model = "qwen2.5:3b"  # 7b 대신
config.models.classification_model = "qwen2.5:1.5b"  # 3b 대신
```

#### RAM 부족
```bash
# 양자화된 모델 사용
ollama pull qwen2.5:7b-q4_0  # 4bit 양자화
```

## 📞 지원

문제가 지속되면:
1. GitHub Issues에 문제 보고
2. 로그 파일 확인: `logs/` 디렉토리
3. 설정 파일 확인: `config/config.json`

## 다음 단계

설정이 완료되면:
1. `python main.py` 실행하여 서비스 시작
2. `http://localhost:8000` 접속
3. API 문서: `http://localhost:8000/docs`