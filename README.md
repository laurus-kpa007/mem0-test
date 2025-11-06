# 🧠 mem0 LTM System - 당신을 기억하는 AI

인간의 장기 기억(Long-Term Memory)을 모방한 AI 메모리 시스템

## 🎯 핵심 특징

mem0는 단순히 데이터를 저장하는 것이 아니라, **인간처럼 기억하고 활용**합니다:

- ✅ **자동 정보 추출**: 대화에서 중요한 정보 자동 파악
- ✅ **메모리 활용**: 저장된 정보를 실제 대화에 활용
- ✅ **지능형 업데이트**: 정보가 변경되면 자동으로 업데이트
- ✅ **관련성 검색**: 문맥에 맞는 관련 정보 제공
- ✅ **중복 제거**: 의미적으로 같은 정보는 통합

## 🚀 빠른 시작

### 1. 설치
```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 2. 패키지 설치
pip install -r requirements-minimal.txt

# 3. Ollama 실행 (별도 터미널)
ollama serve

# 4. 모델 설정
python setup_models.py
```

### 2. 실행 방법

#### 🌐 웹 UI (추천)
```bash
streamlit run app.py
```
브라우저에서 `http://localhost:8501` 접속

#### 🎮 빠른 데모
```bash
python quick_demo.py
```
선택:
1. 자동 데모 - 시나리오 자동 실행
2. 대화형 데모 - 직접 대화

#### 🧪 전체 테스트
```bash
# Windows
run_tests.bat

# 개별 테스트
python test_mem0_core_features.py  # 핵심 기능
python test_enhanced_chat.py       # 메모리 활용
```

## 💬 사용 예시

### 예시 1: 자기소개와 기억
```
You: 안녕하세요, 저는 김철수입니다. 30살 개발자예요.
AI: 안녕하세요 김철수님! 개발자시군요. 반갑습니다.

[다음 대화]
You: 제 이름 기억하시나요?
AI: 네, 김철수님! 30살 개발자시라고 하셨죠.
```

### 예시 2: 선호도 기반 추천
```
You: 저는 커피를 좋아하고 매운 음식은 싫어해요.
AI: 알겠습니다. 커피를 좋아하시고 매운 음식은 피하시는군요.

[다음 대화]
You: 점심 메뉴 추천해주세요.
AI: 매운 음식을 싫어하시니 담백한 메뉴는 어떠세요? 식후 커피도 좋겠네요!
```

### 예시 3: 정보 업데이트
```
You: 저는 주니어 개발자입니다.
[시간 경과]
You: 이제 시니어 개발자가 되었어요!
AI: 축하드립니다! 주니어에서 시니어 개발자가 되셨군요!
```

## 📂 프로젝트 구조

```
mem0-test/
├── app.py                      # 🌐 Streamlit 웹 UI
├── quick_demo.py              # 🎮 빠른 데모 스크립트
├── core/
│   ├── chat_service_enhanced.py  # 메모리 활용 채팅
│   ├── memory_manager_simple.py  # 메모리 관리
│   └── classification_service.py # 자동 분류
├── config/
│   └── settings.py            # 설정 관리
├── data/
│   ├── chroma_db/            # 벡터 DB
│   └── local_memories.json   # 로컬 백업
├── docs/
│   ├── mem0-core-features.md # 핵심 기능 설명
│   └── requirements-specification.md
└── tests/
    ├── test_mem0_core_features.py  # 핵심 기능 테스트
    └── test_enhanced_chat.py        # 메모리 활용 테스트
```

## 🧪 테스트 포인트

### mem0의 10가지 핵심 기능
1. **메모리 추가** - 새 정보 저장
2. **메모리 업데이트** - 정보 변경 시 자동 수정
3. **중복 제거** - 의미적으로 같은 정보 통합
4. **관련성 검색** - 문맥 기반 검색
5. **선택적 삭제** - 불필요한 정보 제거
6. **지속성** - 재시작 후에도 유지
7. **컨텍스트 구성** - 여러 정보 조합
8. **자동 추출** - 대화에서 정보 자동 파악
9. **자동 분류** - 카테고리별 정리
10. **메모리 진화** - 시간에 따른 변화 추적

## 🎯 실제 활용 시나리오

### 개인 비서
- 일정, 선호도, 습관 기억
- 맞춤형 추천 제공

### 고객 서비스
- 고객 정보 자동 파악
- 이전 대화 기반 응대

### 교육 도우미
- 학습 진도 추적
- 개인별 맞춤 학습

## ⚠️ 주의사항

1. **Ollama 필수**
   ```bash
   ollama serve  # 항상 실행 상태 유지
   ```

2. **모델 설치**
   ```bash
   ollama pull qwen2.5:3b
   ollama pull nomic-embed-text
   ```

3. **Python 버전**
   - Python 3.9 ~ 3.12 권장
   - 3.13은 일부 패키지 호환성 문제 가능

## 🔧 문제 해결

### 메모리가 저장되지 않음
- `data/local_memories.json` 파일 확인
- 쓰기 권한 확인

### 메모리가 활용되지 않음
- `app.py`에서 `EnhancedChatService` 사용 확인
- `test_enhanced_chat.py`로 동작 테스트

### Ollama 연결 실패
- `ollama serve` 실행 확인
- http://localhost:11434 접속 테스트

## 📚 더 알아보기

- [mem0 핵심 기능 문서](docs/mem0-core-features.md)
- [기술 아키텍처](docs/technical-architecture.md)
- [요구사항 명세](docs/requirements-specification.md)

## 🤝 기여

이 프로젝트는 [mem0](https://github.com/mem0ai/mem0)를 기반으로 합니다.

## 📜 라이선스

MIT License

---

**💡 핵심 가치**: mem0는 단순한 챗봇이 아닌, 당신을 진정으로 기억하는 AI입니다.