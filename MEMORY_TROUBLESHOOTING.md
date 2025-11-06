# 🔍 메모리 저장 문제 해결 가이드

## 메모리 확인 방법

### 방법 1: 진단 도구 실행
```bash
python check_memory.py
```
이 도구는 다음을 확인합니다:
- 로컬 메모리 파일 존재 여부
- 저장된 메모리 내용
- ChromaDB 상태
- 설정 파일
- 실제 저장 테스트

### 방법 2: 실시간 모니터링
```bash
python monitor_memory.py
```
선택 1: 실시간으로 메모리 변화 관찰
선택 2: 현재 저장된 메모리 확인

### 방법 3: 파일 직접 확인
```bash
# Windows
type data\local_memories.json

# Mac/Linux
cat data/local_memories.json
```

## 📂 메모리 저장 위치

1. **로컬 백업**: `data/local_memories.json`
   - JSON 형식으로 모든 메모리 저장
   - 직접 열어서 확인 가능

2. **벡터 DB**: `data/chroma_db/`
   - ChromaDB 파일들
   - 임베딩 벡터 저장

## ❌ 메모리가 저장되지 않는 경우

### 1. 자동 저장 조건 확인
메모리가 자동으로 저장되려면 다음 중 하나를 포함해야 합니다:

#### 키워드 (더 넓은 범위로 업데이트됨):
- 개인정보: 이름, 나이, 살, 직업, 일, 회사
- 선호도: 좋아, 싫어, 관심, 취미, 즐겨, 선호
- 위치: 사는, 거주, 출신, 살아, 집
- 학력: 공부, 전공, 학교, 대학, 졸업
- 관계: 가족, 부모, 형제, 자매, 친구
- 활동: 음식, 먹, 마시, 여행, 운동, 스포츠
- 문화: 영화, 책, 음악, 게임

#### 패턴:
- "저는", "제가", "나는", "내가"
- "저의", "나의", "제", "내"
- "있습니다", "있어요", "합니다", "해요"

### 2. 메시지 예시

✅ **저장되는 메시지**:
- "저는 김철수입니다"
- "커피를 좋아해요"
- "서울에 살고 있습니다"
- "개발자로 일하고 있어요"

❌ **저장되지 않는 메시지**:
- "안녕"
- "뭐해?"
- "그래"
- "응"

### 3. 디버그 로그 확인

`logs/app.log` 파일에서 다음을 확인:
```
✅ 메모리 자동 저장 완료: ID=...
현재 총 메모리 수: X개
```

### 4. 수동 메모리 추가
웹 UI 왼쪽 사이드바에서:
1. "➕ 메모리 추가" 섹션
2. 정보 입력 (예: "저는 홍길동입니다")
3. "메모리 저장" 버튼 클릭

## 🛠️ 문제 해결 단계

### 단계 1: 폴더 권한 확인
```bash
# data 폴더가 있는지 확인
dir data  # Windows
ls -la data  # Mac/Linux

# 없으면 생성
mkdir data
```

### 단계 2: 설정 초기화
```bash
# Windows
reset_config.bat

# Mac/Linux
./reset_config.sh
```

### 단계 3: 테스트
```bash
# 간단한 테스트
python test_enhanced_chat.py

# 전체 테스트
python test_mem0_core_features.py
```

### 단계 4: 웹에서 테스트
1. `streamlit run app.py`
2. 다음 메시지 입력:
   - "안녕하세요, 저는 테스트입니다"
   - "저는 개발자입니다"
   - "커피를 좋아해요"
3. 오른쪽 패널에서 메모리 확인
4. "📋 메모리 목록 새로고침" 클릭

## 📊 메모리 상태 확인 체크리스트

- [ ] `data` 폴더 존재
- [ ] `data/local_memories.json` 파일 존재
- [ ] 파일 크기 > 0 bytes
- [ ] Ollama 실행 중 (`ollama serve`)
- [ ] 모델 설치됨 (`ollama list`)
- [ ] 웹 UI에서 오른쪽 패널에 메모리 표시
- [ ] 대화 후 "메모리 목록 새로고침" 시 변화

## 💡 팁

1. **강제 저장**: 메시지에 "저는" 또는 "제가"를 포함시키면 거의 확실히 저장됨

2. **카테고리 확인**: 저장된 메모리의 카테고리를 확인하여 분류가 제대로 되는지 확인

3. **실시간 모니터링**: 별도 터미널에서 `python monitor_memory.py` 실행하고 1번 선택하면 메모리 변화를 실시간으로 볼 수 있음

4. **로그 활용**: `logs/app.log`를 tail로 보면서 실시간 로그 확인
   ```bash
   # Windows PowerShell
   Get-Content logs\app.log -Wait -Tail 10

   # Mac/Linux
   tail -f logs/app.log
   ```

## 🚨 그래도 안 되면?

1. **전체 리셋**:
   ```bash
   # data 폴더 삭제 후 재생성
   rmdir /s data  # Windows
   rm -rf data    # Mac/Linux
   mkdir data

   # 설정 재초기화
   python setup_models.py
   ```

2. **Issue 보고**:
   다음 정보와 함께 문제 보고:
   - `python check_memory.py` 출력 결과
   - `logs/app.log` 마지막 부분
   - 입력한 메시지 예시

---

이 가이드를 따라도 문제가 해결되지 않으면 구체적인 오류 메시지와 함께 알려주세요! 🤝