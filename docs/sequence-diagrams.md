# 시퀀스 다이어그램 상세 설계

## 1. 사용자 시나리오별 시퀀스 다이어그램

### 1.1 초기 사용자 온보딩 플로우

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant Auth
    participant MemoryService
    participant InitService
    participant DB

    User->>UI: 첫 방문
    UI->>API: GET /onboarding/status
    API->>Auth: 신규 사용자 확인
    Auth-->>API: 신규 사용자
    API-->>UI: 온보딩 필요

    UI->>UI: 온보딩 화면 표시
    User->>UI: 기본 정보 입력<br/>(이름, 관심사 등)
    UI->>API: POST /onboarding/profile

    API->>InitService: 프로필 초기화
    InitService->>DB: 사용자 생성
    InitService->>MemoryService: 초기 메모리 생성

    loop 기본 질문
        InitService->>UI: 질문 전송
        User->>UI: 답변 입력
        UI->>API: POST /onboarding/answer
        API->>MemoryService: 메모리 저장
    end

    InitService-->>API: 온보딩 완료
    API-->>UI: 메인 화면 이동
```

### 1.2 대화 중 동적 메모리 업데이트

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant LLM
    participant MemoryDetector
    participant ConflictResolver
    participant MemoryService
    participant VectorDB

    User->>UI: "아 맞다, 내가 지난번에<br/>말한 나이가 틀렸어.<br/>30살이 아니라 31살이야"
    UI->>API: POST /chat

    API->>MemoryDetector: 업데이트 감지
    MemoryDetector->>MemoryDetector: 수정 의도 파악
    MemoryDetector-->>API: UPDATE_REQUIRED

    API->>MemoryService: 기존 메모리 검색
    MemoryService->>VectorDB: 나이 관련 메모리
    VectorDB-->>MemoryService: 기존: "나이: 30살"

    MemoryService->>ConflictResolver: 충돌 해결
    ConflictResolver->>ConflictResolver: 신뢰도 평가
    Note over ConflictResolver: 최신 정보 우선<br/>명시적 수정 요청

    ConflictResolver-->>MemoryService: 업데이트 승인
    MemoryService->>VectorDB: 메모리 업데이트

    MemoryService->>MemoryService: 히스토리 생성
    Note over MemoryService: 변경 이력 보존

    API->>LLM: 응답 생성
    LLM-->>API: "알겠습니다. 31살로<br/>정보를 수정했습니다"
    API-->>UI: 응답 + 업데이트 알림
```

### 1.3 복잡한 메모리 연결 플로우

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant MemoryService
    participant RelationMapper
    participant GraphDB
    participant LLM

    User->>UI: "내가 작년 제주도 여행에서<br/>만난 그 친구 기억나?<br/>그 친구가 추천한 카페 가고 싶어"
    UI->>API: POST /chat

    API->>MemoryService: 컨텍스트 검색

    par 병렬 검색
        MemoryService->>GraphDB: "제주도 여행" 검색
        and
        MemoryService->>GraphDB: "친구" 관계 검색
        and
        MemoryService->>GraphDB: "카페" 검색
    end

    GraphDB-->>MemoryService: 메모리 노드들

    MemoryService->>RelationMapper: 관계 분석
    RelationMapper->>RelationMapper: 그래프 탐색
    Note over RelationMapper: 제주도(2023.5) → 김철수 → 카페추천

    RelationMapper-->>MemoryService: 연결된 메모리 체인

    MemoryService-->>API: 컨텍스트 구성
    Note over API: - 2023년 5월 제주도<br/>- 김철수 만남<br/>- "카페 델문도" 추천

    API->>LLM: 풍부한 컨텍스트 전달
    LLM-->>API: "김철수씨가 추천한<br/>카페 델문도 말씀이시죠?<br/>성산일출봉 근처에 있는..."

    API-->>UI: 응답 + 관련 메모리
```

### 1.4 대량 메모리 임포트 처리

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant ImportService
    participant Parser
    participant Classifier
    participant DedupService
    participant MemoryService
    participant Queue

    User->>UI: 파일 업로드 (CSV/JSON)
    UI->>API: POST /import/file

    API->>ImportService: 임포트 시작
    ImportService->>Queue: 작업 큐 등록
    ImportService-->>API: 작업 ID 반환
    API-->>UI: 처리중 상태

    activate Queue
    Queue->>Parser: 파일 파싱

    loop 각 항목 처리
        Parser->>Classifier: 항목 분류
        Classifier->>Classifier: 카테고리 결정

        Classifier->>DedupService: 중복 검사
        DedupService->>MemoryService: 유사 메모리 검색

        alt 중복 발견
            DedupService->>DedupService: 병합 전략 결정
            DedupService->>MemoryService: 기존 메모리 업데이트
        else 신규 메모리
            DedupService->>MemoryService: 새 메모리 생성
        end

        MemoryService-->>Queue: 처리 완료
        Queue->>API: 진행률 업데이트
        API->>UI: SSE/WebSocket 진행률
    end

    deactivate Queue

    Queue-->>ImportService: 임포트 완료
    ImportService->>ImportService: 통계 생성
    ImportService-->>API: 결과 리포트
    API-->>UI: 완료 알림
```

### 1.5 지능형 메모리 추천 시스템

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant RecommendService
    participant PatternAnalyzer
    participant ML_Model
    participant MemoryService
    participant Cache

    User->>UI: 일반 대화 진행
    UI->>API: POST /chat

    API->>RecommendService: 추천 요청

    RecommendService->>Cache: 최근 컨텍스트 확인
    Cache-->>RecommendService: 최근 10개 대화

    RecommendService->>PatternAnalyzer: 패턴 분석
    PatternAnalyzer->>PatternAnalyzer: 주제 추출
    PatternAnalyzer->>PatternAnalyzer: 시간대 분석
    PatternAnalyzer->>PatternAnalyzer: 감정 상태 파악

    PatternAnalyzer->>ML_Model: 추천 예측
    ML_Model->>ML_Model: 협업 필터링
    ML_Model->>ML_Model: 컨텐츠 기반 필터링

    ML_Model-->>RecommendService: 추천 메모리 ID

    RecommendService->>MemoryService: 메모리 조회
    MemoryService-->>RecommendService: 메모리 상세

    RecommendService->>RecommendService: 관련성 재평가
    RecommendService-->>API: Top-3 추천

    API-->>UI: 응답 + 추천 메모리
    UI->>UI: 사이드바에 추천 표시
```

### 1.6 메모리 수명 주기 관리

```mermaid
sequenceDiagram
    participant Scheduler
    participant LifecycleManager
    participant MemoryService
    participant ArchiveService
    participant MetricsService
    participant DB

    Scheduler->>LifecycleManager: 일일 작업 시작

    LifecycleManager->>MemoryService: 메모리 상태 조회
    MemoryService->>DB: 전체 메모리 스캔
    DB-->>MemoryService: 메모리 목록

    loop 각 메모리 평가
        LifecycleManager->>MetricsService: 사용 빈도 확인
        MetricsService-->>LifecycleManager: 접근 통계

        alt 장기 미사용 (90일+)
            LifecycleManager->>ArchiveService: 아카이브 이동
            ArchiveService->>DB: 콜드 스토리지
        else if 낮은 관련성
            LifecycleManager->>MemoryService: 중요도 하향
            MemoryService->>DB: 메타데이터 업데이트
        else if 자주 사용
            LifecycleManager->>MemoryService: 중요도 상향
            MemoryService->>Cache: 캐시 등록
        else
            LifecycleManager->>LifecycleManager: 유지
        end
    end

    LifecycleManager->>LifecycleManager: 통계 생성
    LifecycleManager-->>Scheduler: 작업 완료
```

### 1.7 실시간 협업 메모리 동기화

```mermaid
sequenceDiagram
    participant User1
    participant User2
    participant UI1
    participant UI2
    participant API
    participant SyncService
    participant ConflictResolver
    participant WebSocket
    participant DB

    Note over User1, User2: 공유 메모리 공간

    User1->>UI1: 메모리 수정
    UI1->>API: PUT /memory/{id}

    API->>SyncService: 변경 감지
    SyncService->>DB: 낙관적 잠금 확인

    alt 잠금 성공
        SyncService->>DB: 메모리 업데이트
        SyncService->>WebSocket: 변경 브로드캐스트

        WebSocket->>UI2: 실시간 업데이트
        UI2->>UI2: 화면 갱신
        UI2-->>User2: 변경 알림
    else 동시 수정 충돌
        SyncService->>ConflictResolver: 충돌 해결

        ConflictResolver->>ConflictResolver: 3-way merge
        Note over ConflictResolver: Base ← Change1<br/>Base ← Change2<br/>Merge 시도

        alt 자동 병합 가능
            ConflictResolver->>DB: 병합된 버전 저장
            ConflictResolver->>WebSocket: 양쪽 업데이트
        else 수동 해결 필요
            ConflictResolver->>UI1: 충돌 알림
            ConflictResolver->>UI2: 충돌 알림

            User1->>UI1: 충돌 해결 선택
            UI1->>API: POST /resolve
            API->>SyncService: 최종 버전 확정
        end
    end

    SyncService-->>API: 동기화 완료
```

## 2. 에러 처리 시퀀스

### 2.1 메모리 저장 실패 복구

```mermaid
sequenceDiagram
    participant UI
    participant API
    participant MemoryService
    participant VectorDB
    participant MetaDB
    participant Queue
    participant Fallback

    UI->>API: POST /memory
    API->>MemoryService: 저장 요청

    MemoryService->>VectorDB: 벡터 저장
    VectorDB--xMemoryService: 연결 오류

    MemoryService->>Queue: 재시도 큐 등록
    Queue-->>MemoryService: 큐 등록 완료

    MemoryService->>Fallback: 임시 저장
    Fallback->>Fallback: 로컬 파일 저장

    MemoryService-->>API: 부분 성공
    API-->>UI: 저장 지연 알림

    loop 재시도 (3회)
        Queue->>VectorDB: 재시도
        alt 성공
            VectorDB-->>Queue: 저장 완료
            Queue->>Fallback: 임시 데이터 삭제
            Queue->>API: 완료 알림
            API->>UI: 성공 알림
        else 실패
            Queue->>Queue: 대기 후 재시도
        end
    end

    Note over Queue: 최종 실패 시<br/>관리자 알림
```

### 2.2 LLM 응답 실패 처리

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant LLM_Primary
    participant LLM_Fallback
    participant Cache
    participant TemplateEngine

    User->>UI: 질문 입력
    UI->>API: POST /chat

    API->>LLM_Primary: 응답 요청 (타임아웃 5초)
    LLM_Primary--xAPI: 타임아웃/오류

    API->>Cache: 유사 질문 캐시 확인

    alt 캐시 히트
        Cache-->>API: 캐시된 응답
        API->>API: 응답 변형
        API-->>UI: 캐시 기반 응답
    else 캐시 미스
        API->>LLM_Fallback: 백업 모델 시도

        alt 백업 성공
            LLM_Fallback-->>API: 응답
            API-->>UI: 백업 모델 응답
        else 백업도 실패
            API->>TemplateEngine: 템플릿 응답
            TemplateEngine-->>API: 기본 응답
            API-->>UI: "일시적인 문제가 발생했습니다"
        end
    end

    API->>API: 오류 로깅
    API->>API: 메트릭 기록
```

## 3. 성능 최적화 시퀀스

### 3.1 캐싱 전략 실행

```mermaid
sequenceDiagram
    participant Client
    participant CDN
    participant API
    participant L1_Cache
    participant L2_Cache
    participant L3_Cache
    participant DB

    Client->>CDN: 정적 리소스 요청

    alt CDN 히트
        CDN-->>Client: 캐시된 리소스
    else CDN 미스
        CDN->>API: 리소스 요청
        API->>L1_Cache: 메모리 캐시 확인

        alt L1 히트
            L1_Cache-->>API: 즉시 반환
        else L1 미스
            API->>L2_Cache: Redis 캐시 확인

            alt L2 히트
                L2_Cache-->>API: 캐시 데이터
                API->>L1_Cache: L1 캐시 업데이트
            else L2 미스
                API->>L3_Cache: 디스크 캐시 확인

                alt L3 히트
                    L3_Cache-->>API: 캐시 데이터
                    API->>L2_Cache: L2 캐시 업데이트
                    API->>L1_Cache: L1 캐시 업데이트
                else 전체 미스
                    API->>DB: 데이터베이스 조회
                    DB-->>API: 원본 데이터

                    par 캐시 업데이트
                        API->>L1_Cache: 저장
                        and
                        API->>L2_Cache: 저장
                        and
                        API->>L3_Cache: 저장
                    end
                end
            end
        end

        API-->>CDN: 데이터 반환
        CDN->>CDN: CDN 캐시 저장
        CDN-->>Client: 응답
    end
```

### 3.2 벡터 검색 최적화

```mermaid
sequenceDiagram
    participant API
    participant SearchOptimizer
    participant Embedder
    participant IndexManager
    participant VectorDB
    participant Quantizer
    participant Cache

    API->>SearchOptimizer: 검색 요청

    SearchOptimizer->>Cache: 임베딩 캐시 확인

    alt 캐시 히트
        Cache-->>SearchOptimizer: 캐시된 임베딩
    else 캐시 미스
        SearchOptimizer->>Embedder: 텍스트 임베딩
        Embedder-->>SearchOptimizer: 벡터
        SearchOptimizer->>Cache: 캐시 저장
    end

    SearchOptimizer->>IndexManager: 인덱스 선택
    IndexManager->>IndexManager: 데이터 크기 확인

    alt 소규모 (<1000)
        IndexManager-->>SearchOptimizer: Flat Index
    else if 중규모 (<100K)
        IndexManager-->>SearchOptimizer: IVF Index
    else 대규모
        IndexManager-->>SearchOptimizer: HNSW Index
    end

    SearchOptimizer->>Quantizer: 벡터 양자화
    Quantizer-->>SearchOptimizer: 압축된 벡터

    SearchOptimizer->>VectorDB: 최적화된 검색
    VectorDB->>VectorDB: ANN 검색
    VectorDB-->>SearchOptimizer: Top-K 결과

    SearchOptimizer->>SearchOptimizer: 후처리
    SearchOptimizer-->>API: 최종 결과
```

## 4. 보안 시퀀스

### 4.1 Zero-Trust 인증 플로우

```mermaid
sequenceDiagram
    participant User
    participant Client
    participant API_Gateway
    participant Auth_Service
    participant Token_Service
    participant MFA_Service
    participant Resource

    User->>Client: 로그인 시도
    Client->>API_Gateway: POST /auth/login

    API_Gateway->>Auth_Service: 1차 인증
    Auth_Service->>Auth_Service: 비밀번호 검증

    Auth_Service->>MFA_Service: MFA 요청
    MFA_Service-->>Client: OTP 요청
    User->>Client: OTP 입력
    Client->>MFA_Service: OTP 검증
    MFA_Service-->>Auth_Service: MFA 성공

    Auth_Service->>Token_Service: 토큰 생성
    Token_Service->>Token_Service: Access Token (15분)
    Token_Service->>Token_Service: Refresh Token (7일)

    Token_Service-->>Client: 토큰 쌍 반환

    Note over Client: 이후 API 호출

    Client->>API_Gateway: API 요청 + Access Token
    API_Gateway->>Token_Service: 토큰 검증

    Token_Service->>Token_Service: 서명 검증
    Token_Service->>Token_Service: 만료 확인
    Token_Service->>Token_Service: 권한 확인

    Token_Service-->>API_Gateway: 검증 완료
    API_Gateway->>Resource: 요청 전달
    Resource-->>Client: 응답
```

## 5. 모니터링 및 로깅 시퀀스

### 5.1 분산 추적 플로우

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service_A
    participant Service_B
    participant DB
    participant Tracer
    participant Collector

    Client->>API: 요청 (Trace ID 생성)
    API->>Tracer: Span 시작

    API->>Service_A: 호출 (Trace ID 전파)
    Service_A->>Tracer: Child Span 시작

    Service_A->>Service_B: 호출 (Trace ID 전파)
    Service_B->>Tracer: Child Span 시작

    Service_B->>DB: 쿼리
    DB-->>Service_B: 결과

    Service_B->>Tracer: Span 종료
    Service_B-->>Service_A: 응답

    Service_A->>Tracer: Span 종료
    Service_A-->>API: 응답

    API->>Tracer: Span 종료
    API-->>Client: 최종 응답

    Tracer->>Collector: Trace 데이터 전송
    Collector->>Collector: 집계 및 분석

    Note over Collector: 성능 분석<br/>병목 지점 식별<br/>에러 추적
```

## 다음 단계

1. 구현 우선순위 결정
2. 프로토타입 개발 시작
3. 성능 테스트 시나리오 작성
4. 보안 감사 체크리스트 준비