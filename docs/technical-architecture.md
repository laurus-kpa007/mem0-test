# 기술 아키텍처 설계 문서

## 1. 시스템 아키텍처 개요

### 1.1 전체 시스템 구성도

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Web UI<br/>React/Streamlit]
        UI_Chat[Chat Interface]
        UI_Memory[Memory Dashboard]
        UI_Input[Memory Input]

        UI --> UI_Chat
        UI --> UI_Memory
        UI --> UI_Input
    end

    subgraph "API Gateway"
        API[FastAPI Server]
        Auth[Authentication]
        RateLimit[Rate Limiter]

        API --> Auth
        API --> RateLimit
    end

    subgraph "Core Services"
        MS[Memory Service]
        CS[Classification Service]
        SS[Search Service]
        PS[Processing Service]

        MS --> Memory_Manager[Memory Manager]
        CS --> Auto_Classifier[Auto Classifier]
        SS --> Context_Search[Context Search]
        PS --> Pipeline[Processing Pipeline]
    end

    subgraph "AI/ML Layer"
        LLM[Ollama<br/>Local LLM]
        NLP[NLP Engine]
        Embedder[Embedding Model]

        LLM --> Model[llama2/mistral/qwen]
        NLP --> NER[Named Entity Recognition]
        NLP --> Sentiment[Sentiment Analysis]
    end

    subgraph "Memory Layer"
        Mem0[mem0<br/>Memory Core]
        VectorDB[(Vector Database<br/>Qdrant/Chroma)]
        MetaDB[(Metadata DB<br/>SQLite/PostgreSQL)]
        Cache[(Redis Cache<br/>Optional)]
    end

    subgraph "Storage Layer"
        FileStore[File Storage]
        Backup[Backup Service]

        FileStore --> JSON_Files[JSON Files]
        FileStore --> CSV_Files[CSV Files]
        FileStore --> Media_Files[Media Files]
    end

    UI_Chat <--> API
    UI_Memory <--> API
    UI_Input <--> API

    API <--> MS
    API <--> CS
    API <--> SS
    API <--> PS

    MS <--> Mem0
    CS <--> NLP
    SS <--> Embedder
    PS <--> LLM

    Mem0 <--> VectorDB
    MS <--> MetaDB
    MS <--> Cache

    MS <--> FileStore
    FileStore <--> Backup

    style UI fill:#e1f5fe
    style API fill:#fff3e0
    style MS fill:#f3e5f5
    style LLM fill:#e8f5e9
    style Mem0 fill:#fce4ec
    style FileStore fill:#f5f5f5
```

### 1.2 컴포넌트 계층 구조

```mermaid
graph LR
    subgraph "Presentation"
        Web[Web Interface]
        API_Gateway[API Gateway]
    end

    subgraph "Business Logic"
        Memory_Logic[Memory Logic]
        Classification_Logic[Classification Logic]
        Search_Logic[Search Logic]
    end

    subgraph "Data Processing"
        NLP_Process[NLP Processing]
        Embedding_Process[Embedding]
        LLM_Process[LLM Processing]
    end

    subgraph "Data Access"
        Memory_Store[Memory Storage]
        Vector_Store[Vector Storage]
        Meta_Store[Metadata Storage]
    end

    Web --> API_Gateway
    API_Gateway --> Memory_Logic
    API_Gateway --> Classification_Logic
    API_Gateway --> Search_Logic

    Memory_Logic --> NLP_Process
    Classification_Logic --> NLP_Process
    Search_Logic --> Embedding_Process

    Memory_Logic --> LLM_Process

    NLP_Process --> Memory_Store
    Embedding_Process --> Vector_Store
    LLM_Process --> Meta_Store
```

## 2. 데이터 플로우 다이어그램

### 2.1 메모리 자동 저장 플로우

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant MemoryService
    participant LLM
    participant NLP
    participant mem0
    participant VectorDB
    participant MetaDB

    User->>UI: 대화 입력
    UI->>API: POST /chat
    API->>LLM: 응답 생성
    LLM-->>API: AI 응답
    API-->>UI: 응답 표시

    API->>MemoryService: 메모리 추출 요청
    MemoryService->>NLP: 텍스트 분석
    NLP-->>MemoryService: 엔티티, 감정, 키워드

    MemoryService->>mem0: 메모리 저장
    mem0->>VectorDB: 벡터 임베딩 저장
    mem0->>MetaDB: 메타데이터 저장

    MemoryService-->>API: 저장 완료
    API-->>UI: 메모리 저장 알림
```

### 2.2 수동 메모리 입력 및 자동 분류 플로우

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant ClassificationService
    participant NLP
    participant MemoryService
    participant mem0
    participant VectorDB

    User->>UI: 메모리 수동 입력
    UI->>API: POST /memory/manual
    API->>ClassificationService: 분류 요청

    ClassificationService->>NLP: 텍스트 분석
    NLP-->>ClassificationService: NER 결과
    NLP-->>ClassificationService: 감정 분석
    NLP-->>ClassificationService: 키워드 추출

    ClassificationService->>ClassificationService: 카테고리 결정
    ClassificationService->>ClassificationService: 중복 검사

    ClassificationService-->>API: 분류 결과
    API-->>UI: 분류 결과 표시

    User->>UI: 확인/수정
    UI->>API: POST /memory/save

    API->>MemoryService: 저장 요청
    MemoryService->>mem0: 메모리 저장
    mem0->>VectorDB: 벡터 저장

    MemoryService-->>API: 저장 완료
    API-->>UI: 저장 성공
```

### 2.3 메모리 검색 및 활용 플로우

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant SearchService
    participant Embedder
    participant VectorDB
    participant MemoryService
    participant LLM

    User->>UI: 질문 입력
    UI->>API: POST /chat

    API->>SearchService: 관련 메모리 검색
    SearchService->>Embedder: 질문 임베딩
    Embedder-->>SearchService: 벡터 생성

    SearchService->>VectorDB: 유사도 검색
    VectorDB-->>SearchService: Top-K 결과

    SearchService->>MemoryService: 메모리 상세 조회
    MemoryService-->>SearchService: 메모리 내용

    SearchService-->>API: 관련 메모리

    API->>LLM: 컨텍스트 + 질문
    Note over LLM: 메모리 기반<br/>응답 생성
    LLM-->>API: 개인화된 응답

    API-->>UI: 응답 + 사용된 메모리
    UI-->>User: 결과 표시
```

## 3. 메모리 처리 파이프라인

### 3.1 처리 단계별 플로우

```mermaid
graph TD
    Input[입력 텍스트]

    subgraph "1. Parsing"
        P1[텍스트 정규화]
        P2[언어 감지]
        P3[구조 분석]
        P1 --> P2 --> P3
    end

    subgraph "2. Extraction"
        E1[NER 처리]
        E2[날짜/시간 추출]
        E3[키워드 추출]
        E4[감정 분석]
        E1 --> E2
        E3 --> E4
    end

    subgraph "3. Classification"
        C1[카테고리 매칭]
        C2[중요도 평가]
        C3[신뢰도 계산]
        C1 --> C2 --> C3
    end

    subgraph "4. Deduplication"
        D1[기존 메모리 검색]
        D2[유사도 계산]
        D3[병합/업데이트 결정]
        D1 --> D2 --> D3
    end

    subgraph "5. Enrichment"
        En1[컨텍스트 추가]
        En2[관계 매핑]
        En3[태그 생성]
        En1 --> En2 --> En3
    end

    subgraph "6. Storage"
        S1[압축]
        S2[인덱싱]
        S3[저장]
        S1 --> S2 --> S3
    end

    Input --> P1
    P3 --> E1
    P3 --> E3
    E2 --> C1
    E4 --> C1
    C3 --> D1
    D3 --> En1
    En3 --> S1
    S3 --> Output[저장된 메모리]

    style Input fill:#e3f2fd
    style Output fill:#c8e6c9
```

### 3.2 메모리 관계 그래프

```mermaid
graph TD
    subgraph "메모리 노드"
        M1[메모리 1<br/>여행: 제주도]
        M2[메모리 2<br/>음식: 흑돼지]
        M3[메모리 3<br/>사람: 김철수]
        M4[메모리 4<br/>활동: 서핑]
        M5[메모리 5<br/>감정: 행복]
    end

    subgraph "관계 타입"
        R1[caused_by]
        R2[related_to]
        R3[part_of]
        R4[occurred_with]
        R5[emotion_of]
    end

    M1 -.->|related_to| M2
    M1 -.->|occurred_with| M3
    M4 -.->|part_of| M1
    M5 -.->|emotion_of| M1
    M3 -.->|related_to| M4

    style M1 fill:#fff3e0
    style M2 fill:#fce4ec
    style M3 fill:#e8f5e9
    style M4 fill:#e3f2fd
    style M5 fill:#f3e5f5
```

## 4. 데이터베이스 스키마

### 4.1 ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    USER ||--o{ MEMORY : has
    USER ||--o{ SESSION : has
    SESSION ||--o{ CONVERSATION : contains
    MEMORY ||--o{ MEMORY_RELATION : has
    MEMORY ||--o{ MEMORY_TAG : has
    CATEGORY ||--o{ MEMORY : categorizes

    USER {
        string user_id PK
        string username
        string email
        datetime created_at
        datetime last_active
        json preferences
    }

    MEMORY {
        string memory_id PK
        string user_id FK
        string category_id FK
        text content
        json metadata
        float importance
        string memory_type
        datetime created_at
        datetime updated_at
        vector embedding
    }

    CATEGORY {
        string category_id PK
        string name
        string parent_id FK
        json keywords
        int priority
    }

    MEMORY_RELATION {
        string relation_id PK
        string source_memory_id FK
        string target_memory_id FK
        string relation_type
        float strength
        datetime created_at
    }

    MEMORY_TAG {
        string tag_id PK
        string memory_id FK
        string tag_name
        string tag_type
        float confidence
    }

    SESSION {
        string session_id PK
        string user_id FK
        datetime start_time
        datetime end_time
        json session_metadata
    }

    CONVERSATION {
        string conversation_id PK
        string session_id FK
        text user_input
        text ai_response
        json used_memories
        datetime timestamp
    }
```

## 5. API 엔드포인트 구조

### 5.1 RESTful API 설계

```mermaid
graph TD
    subgraph "Chat API"
        Chat[/api/chat]
        Chat --> POST_Chat[POST: 대화 처리]
        Chat --> GET_History[GET: 대화 기록]
    end

    subgraph "Memory API"
        Memory[/api/memory]
        Memory --> POST_Auto[POST: 자동 저장]
        Memory --> POST_Manual[POST: 수동 입력]
        Memory --> GET_Memory[GET: 조회]
        Memory --> PUT_Memory[PUT: 수정]
        Memory --> DELETE_Memory[DELETE: 삭제]
        Memory --> GET_Search[GET: 검색]
    end

    subgraph "Classification API"
        Class[/api/classify]
        Class --> POST_Classify[POST: 분류 요청]
        Class --> GET_Categories[GET: 카테고리 목록]
    end

    subgraph "User API"
        User[/api/user]
        User --> POST_Register[POST: 회원가입]
        User --> POST_Login[POST: 로그인]
        User --> GET_Profile[GET: 프로필]
        User --> PUT_Settings[PUT: 설정 변경]
    end

    subgraph "Export API"
        Export[/api/export]
        Export --> GET_JSON[GET: JSON 내보내기]
        Export --> GET_CSV[GET: CSV 내보내기]
        Export --> POST_Import[POST: 가져오기]
    end
```

## 6. 보안 및 인증 플로우

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant JWT
    participant Service
    participant DB

    Client->>API: POST /login (credentials)
    API->>Auth: 인증 요청
    Auth->>DB: 사용자 확인
    DB-->>Auth: 사용자 정보
    Auth->>JWT: 토큰 생성
    JWT-->>Auth: Access Token
    Auth-->>API: 토큰 반환
    API-->>Client: {token, user_info}

    Note over Client: 이후 요청

    Client->>API: GET /memory (Bearer token)
    API->>JWT: 토큰 검증
    JWT-->>API: 유효성 확인
    API->>Service: 요청 처리
    Service->>DB: 데이터 조회
    DB-->>Service: 결과
    Service-->>API: 응답 데이터
    API-->>Client: 메모리 목록
```

## 7. 성능 최적화 전략

```mermaid
graph TD
    subgraph "Caching Strategy"
        C1[User Session Cache]
        C2[Frequent Memory Cache]
        C3[Embedding Cache]
        C4[Search Result Cache]
    end

    subgraph "Database Optimization"
        D1[Index Optimization]
        D2[Query Optimization]
        D3[Connection Pooling]
        D4[Batch Processing]
    end

    subgraph "Vector Search Optimization"
        V1[HNSW Index]
        V2[Quantization]
        V3[Pruning]
        V4[Sharding]
    end

    subgraph "Processing Optimization"
        P1[Async Processing]
        P2[Queue Management]
        P3[Load Balancing]
        P4[Resource Pooling]
    end

    C1 --> Redis
    C2 --> Redis
    C3 --> Memory
    C4 --> Redis

    D1 --> PostgreSQL
    D2 --> QueryPlanner
    D3 --> ConnectionPool
    D4 --> BatchQueue

    V1 --> Qdrant
    V2 --> Compression
    V3 --> Cleanup
    V4 --> Distribution

    P1 --> Celery
    P2 --> RabbitMQ
    P3 --> Nginx
    P4 --> ThreadPool
```

## 8. 배포 아키텍처

```mermaid
graph TD
    subgraph "Development"
        Dev[Local Development]
        Dev --> Docker_Dev[Docker Compose]
        Docker_Dev --> Local_Services[Local Services]
    end

    subgraph "Staging"
        Stage[Staging Server]
        Stage --> Docker_Stage[Docker Swarm]
        Docker_Stage --> Stage_Services[Stage Services]
    end

    subgraph "Production"
        Prod[Production]
        Prod --> K8s[Kubernetes]
        K8s --> Prod_Services[Prod Services]

        subgraph "K8s Cluster"
            Pod1[API Pods]
            Pod2[Worker Pods]
            Pod3[DB Pods]
            Pod4[Cache Pods]
        end
    end

    Dev --> CI[CI/CD Pipeline]
    CI --> Stage
    Stage --> Testing[Testing]
    Testing --> Prod

    style Dev fill:#e8f5e9
    style Stage fill:#fff3e0
    style Prod fill:#ffebee
```

## 9. 모니터링 및 로깅

```mermaid
graph LR
    subgraph "Application"
        App[FastAPI App]
        Workers[Background Workers]
    end

    subgraph "Logging"
        AppLog[Application Logs]
        AccessLog[Access Logs]
        ErrorLog[Error Logs]
    end

    subgraph "Metrics"
        Prometheus[Prometheus]
        Grafana[Grafana]
    end

    subgraph "Tracing"
        Jaeger[Jaeger]
        OpenTelemetry[OpenTelemetry]
    end

    subgraph "Alerting"
        AlertManager[Alert Manager]
        Slack[Slack/Email]
    end

    App --> AppLog
    App --> Prometheus
    App --> OpenTelemetry

    Workers --> AppLog
    Workers --> Prometheus

    AppLog --> ELK[ELK Stack]
    AccessLog --> ELK
    ErrorLog --> ELK

    Prometheus --> Grafana
    Prometheus --> AlertManager

    OpenTelemetry --> Jaeger

    AlertManager --> Slack
```

## 다음 단계

1. 각 컴포넌트의 상세 인터페이스 정의
2. API 스펙 문서 작성 (OpenAPI)
3. 데이터베이스 마이그레이션 스크립트
4. 도커 컨테이너 설정
5. 개발 환경 구축 가이드