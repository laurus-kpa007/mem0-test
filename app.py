"""
Streamlit 웹 애플리케이션 - mem0 LTM 시스템 UI
초보자도 쉽게 사용할 수 있는 간단한 인터페이스
"""

import streamlit as st
import asyncio
from datetime import datetime
import json
import uuid
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from core.memory_manager_simple import SimpleMemoryManager  # 간소화된 버전 사용
from core.chat_service_enhanced import EnhancedChatService  # 메모리를 실제로 활용하는 강화된 버전
from core.classification_service import ClassificationService
from config.settings import initialize_config, OllamaManager

# 페이지 설정
st.set_page_config(
    page_title="mem0 LTM - 장기 기억 챗봇",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .memory-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)

# 초기화 함수
@st.cache_resource
def initialize_services():
    """서비스 초기화 (한 번만 실행)"""
    try:
        config = initialize_config()
        memory_manager = SimpleMemoryManager(config)
        chat_service = EnhancedChatService(config)  # 강화된 채팅 서비스 사용
        classifier = ClassificationService(config)
        return config, memory_manager, chat_service, classifier
    except Exception as e:
        st.error(f"서비스 초기화 실패: {e}")
        st.stop()

# 서비스 초기화
config, memory_manager, chat_service, classifier = initialize_services()

# 세션 상태 초기화
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memories" not in st.session_state:
    st.session_state.memories = []

# 비동기 함수 실행 헬퍼
def run_async(coro):
    """비동기 함수를 동기적으로 실행"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# 헤더
st.title("🧠 mem0 LTM - 장기 기억 챗봇")
st.markdown("""
**당신을 기억하는 AI** - 대화하면서 자연스럽게 정보를 기억합니다.
예시: "저는 김철수입니다" → 다음 대화에서 "김철수님" 호칭 사용
""")

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")

    # 사용자 정보
    st.subheader("👤 세션 정보")
    st.info(f"사용자 ID: {st.session_state.user_id}")
    st.caption("💡 대화를 통해 자동으로 정보가 저장됩니다")

    st.divider()

    # 메모리 관리
    st.subheader("💾 메모리 관리")

    # 메모리 통계
    try:
        stats = memory_manager.get_statistics(st.session_state.user_id)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 메모리", stats['total_memories'])
        with col2:
            st.metric("카테고리", len(stats['categories']))
    except:
        st.info("아직 저장된 메모리가 없습니다.")

    # 메모리 수동 추가
    st.subheader("➕ 메모리 추가")
    with st.form("add_memory"):
        new_memory = st.text_area(
            "새로운 정보 입력",
            placeholder="예: 저는 파이썬을 좋아합니다",
            height=100
        )
        submitted = st.form_submit_button("메모리 저장")

        if submitted and new_memory:
            # 분류
            category = run_async(classifier.classify_text(new_memory))

            # 저장
            memory_id = run_async(memory_manager.add_memory(
                text=new_memory,
                user_id=st.session_state.user_id,
                metadata={
                    "source": "manual",
                    "category": category
                }
            ))
            st.success(f"✅ 메모리 저장 완료! (카테고리: {category})")
            st.rerun()

    st.divider()

    # 메모리 목록 보기
    if st.button("📋 메모리 목록 새로고침"):
        st.session_state.memories = run_async(
            memory_manager.get_all_memories(st.session_state.user_id, limit=20)
        )

    # 대화 초기화
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        chat_service.clear_session(st.session_state.session_id)
        st.rerun()

# 메인 레이아웃
col1, col2 = st.columns([2, 1])

# 왼쪽: 채팅 인터페이스
with col1:
    st.subheader("💬 대화")

    # 대화 표시 영역
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

                # 사용된 메모리 표시
                if message["role"] == "assistant" and "used_memories" in message:
                    if message["used_memories"]:
                        with st.expander("🔍 참조된 메모리"):
                            for mem in message["used_memories"]:
                                st.write(f"• {mem['text']}")

    # 입력 영역
    user_input = st.chat_input("메시지를 입력하세요...")

    if user_input:
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # 대화 처리
        with st.spinner("생각 중..."):
            response = run_async(chat_service.chat(
                message=user_input,
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id,
                use_memory=True
            ))

        # 응답 추가
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["response"],
            "used_memories": response.get("used_memories", [])
        })

        # 추출된 메모리 표시
        if response.get("extracted_memories"):
            st.success(f"💡 {len(response['extracted_memories'])}개의 새로운 정보를 기억했습니다!")

        st.rerun()

# 오른쪽: 메모리 뷰어
with col2:
    st.subheader("🧠 저장된 메모리")

    # 메모리 검색
    search_query = st.text_input("🔍 메모리 검색", placeholder="검색어 입력...")

    if search_query:
        with st.spinner("검색 중..."):
            search_results = run_async(memory_manager.search_memories(
                query=search_query,
                user_id=st.session_state.user_id,
                limit=10
            ))

        st.write(f"검색 결과: {len(search_results)}개")
        for result in search_results:
            with st.container():
                st.write(f"📝 {result.get('text', '')}")
                metadata = result.get('metadata', {})
                if metadata.get('category'):
                    st.caption(f"카테고리: {metadata['category']}")
                st.divider()
    else:
        # 전체 메모리 표시
        if not st.session_state.memories:
            st.session_state.memories = run_async(
                memory_manager.get_all_memories(st.session_state.user_id, limit=20)
            )

        if st.session_state.memories:
            for memory in st.session_state.memories:
                with st.container():
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.write(f"📝 {memory.get('text', '')}")
                        metadata = memory.get('metadata', {})
                        if metadata.get('category'):
                            st.caption(f"카테고리: {metadata['category']}")
                    with col_b:
                        if st.button("🗑️", key=f"del_{memory.get('id', '')}"):
                            run_async(memory_manager.delete_memory(
                                memory_id=memory['id'],
                                user_id=st.session_state.user_id
                            ))
                            st.rerun()
                    st.divider()
        else:
            st.info("아직 저장된 메모리가 없습니다.")
            st.markdown("""
            **테스트 해보세요:**
            1. "안녕하세요, 저는 홍길동입니다"
            2. "저는 개발자입니다"
            3. "커피를 좋아해요"

            그 다음 물어보세요:
            - "제 이름 아세요?"
            - "제가 뭐 좋아한다고 했죠?"
            """)

# 푸터
st.divider()
st.caption("💡 팁: 대화 중에 언급한 정보는 자동으로 기억됩니다. 수동으로 정보를 추가할 수도 있습니다.")

# 시스템 상태 표시
with st.expander("🔧 시스템 정보"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**대화 모델:** {config.models.chat_model}")
    with col2:
        st.write(f"**임베딩 모델:** {config.models.embedding_model}")
    with col3:
        st.write(f"**세션 ID:** {st.session_state.session_id[:8]}...")

    # Ollama 상태 확인
    ollama_manager = OllamaManager()
    models = ollama_manager.list_models()
    if models:
        st.success(f"✅ Ollama 연결됨 ({len(models)}개 모델)")
    else:
        st.error("❌ Ollama 연결 실패 - 'ollama serve' 실행 확인")