"""
사담(四談) - Fortune Dialogue
AI 손님과 대화를 나누며 사주를 풀어가는 감성 대화형 웹 프로젝트
"""

import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="사담(四談) - Fortune Dialogue",
    page_icon="🪶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for traditional Korean aesthetic
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #8B4513;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .sub-header {
        text-align: center;
        color: #A0826D;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #E8F4F8;
        margin-left: 20%;
    }
    .ai-message {
        background-color: #F5F5DC;
        margin-right: 20%;
    }
    .character-card {
        background-color: #FFF8DC;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 2px solid #D2B48C;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        height: 3rem;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'character' not in st.session_state:
    st.session_state.character = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None

# Header
st.markdown('<div class="main-header">사담(四談)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI와 함께하는 감성 사주 상담</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🎭 메뉴")
    
    if st.button("🆕 새로운 상담 시작"):
        st.session_state.messages = []
        st.session_state.character = None
        st.session_state.session_id = None
        st.rerun()
    
    st.divider()
    
    st.subheader("📜 과거 상담 기록")
    st.info("기능 개발 예정")
    
    st.divider()
    
    st.subheader("⚙️ 설정")
    st.checkbox("배경 음악", value=False, disabled=True)

# Main content area
if st.session_state.character is None:
    # Character generation screen
    st.markdown("### 🪶 상담을 시작하시겠습니까?")
    st.write("새로운 손님이 사주를 보러 찾아왔습니다.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("손님 맞이하기", type="primary", use_container_width=True):
            with st.spinner("손님이 들어오고 있습니다..."):
                # TODO: Generate character using OpenAI
                st.session_state.character = {
                    "name": "임수진",
                    "age": 35,
                    "gender": "여성",
                    "occupation": "프리랜서 일러스트레이터",
                    "personality": "섬세하고 내성적이며 창의적인 성격",
                    "concern": "최근 중요한 클라이언트를 잃고 재정적인 어려움과 진로에 대한 고민을 하고 있음",
                    "birth_date": "1985-07-14",
                    "birth_time": "08:30",
                    "speaking_style": "부드럽고 정중한 말투, 예술적 표현을 자주 사용함"
                }
                st.rerun()
else:
    # Character profile display
    with st.container():
        st.markdown('<div class="character-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image("https://via.placeholder.com/150", caption="인물 이미지")
        
        with col2:
            st.markdown(f"### {st.session_state.character['name']}")
            st.write(f"**나이**: {st.session_state.character['age']}세 | **성별**: {st.session_state.character['gender']}")
            st.write(f"**직업**: {st.session_state.character['occupation']}")
            st.write(f"**성격**: {st.session_state.character['personality']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Chat area
    st.markdown("### 💬 대화")
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>나</strong><br>{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai-message"><strong>{st.session_state.character["name"]}</strong><br>{content}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("메시지를 입력하세요...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # TODO: Generate AI response using OpenAI
        # For now, use a placeholder response
        ai_response = f"({st.session_state.character['name']}) 네, 말씀해 주세요... (AI 응답 기능 개발 예정)"
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()
    
    # End consultation button
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔮 상담 종료 및 사주 결과 보기", use_container_width=True):
            st.info("사주 해석 기능은 개발 예정입니다.")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888; font-size: 0.9em;">사담(四談) - Fortune Dialogue | Powered by OpenAI & Supabase</div>',
    unsafe_allow_html=True
)