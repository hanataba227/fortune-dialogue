"""
사담(四談) - Fortune Dialogue
AI 손님과 대화를 나누며 사주를 풀어가는 감성 대화형 웹 프로젝트
"""

import streamlit as st
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.openai_helper import generate_character_profile, chat_with_character
from utils.supabase_helper import (
    create_character, create_session, save_message, 
    end_session, get_conversation_history
)

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
if 'character_id' not in st.session_state:
    st.session_state.character_id = None
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
        st.session_state.character_id = None
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
                # Generate character using OpenAI
                character_data = generate_character_profile()
                
                if character_data:
                    # Save character to database
                    character_id = create_character(character_data)
                    
                    if character_id:
                        # Create session
                        session_id = create_session(character_id)
                        
                        if session_id:
                            st.session_state.character = character_data
                            st.session_state.character_id = character_id
                            st.session_state.session_id = session_id
                            
                            # Add initial greeting message
                            greeting = f"안녕하세요... 저는 {character_data['name']}이라고 합니다. 사주를 보러 왔어요."
                            st.session_state.messages.append({"role": "assistant", "content": greeting})
                            save_message(session_id, character_id, "ai", greeting)
                            
                            st.rerun()
                        else:
                            st.error("세션 생성에 실패했습니다.")
                    else:
                        st.error("인물 저장에 실패했습니다.")
                else:
                    st.error("인물 생성에 실패했습니다. 다시 시도해주세요.")
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
        save_message(st.session_state.session_id, st.session_state.character_id, "user", user_input)
        
        # Generate AI response using OpenAI
        with st.spinner(f"{st.session_state.character['name']}님이 생각하고 있습니다..."):
            # Prepare character context
            character_context = f"""
이름: {st.session_state.character['name']}
나이: {st.session_state.character['age']}세
성별: {st.session_state.character['gender']}
직업: {st.session_state.character['occupation']}
성격: {st.session_state.character['personality']}
현재 고민: {st.session_state.character['concern']}
말투: {st.session_state.character['speaking_style']}

당신은 사주를 보러 온 손님입니다. 자연스럽고 진솔하게 대화하세요.
너무 많이 말하지 말고, 간결하게 답변하세요.
"""
            
            # Prepare conversation history for API
            conversation_history = []
            for msg in st.session_state.messages[:-1]:  # Exclude the current user message
                role = "assistant" if msg["role"] == "assistant" else "user"
                conversation_history.append({"role": role, "content": msg["content"]})
            
            # Get AI response
            ai_response = chat_with_character(character_context, user_input, conversation_history)
            
            if ai_response:
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                save_message(st.session_state.session_id, st.session_state.character_id, "ai", ai_response)
            else:
                st.error("응답 생성에 실패했습니다. 다시 시도해주세요.")
        
        st.rerun()
    
    # End consultation button
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔮 상담 종료 및 사주 결과 보기", use_container_width=True):
            if len(st.session_state.messages) > 2:  # At least some conversation happened
                with st.spinner("대화 내용을 분석하고 있습니다..."):
                    # End session
                    end_session(st.session_state.session_id)
                    st.success("상담이 종료되었습니다.")
                    st.info("사주 해석 기능은 Phase 3에서 개발 예정입니다.")
            else:
                st.warning("대화를 더 나눈 후에 상담을 종료해주세요.")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888; font-size: 0.9em;">사담(四談) - Fortune Dialogue | Powered by OpenAI & Supabase</div>',
    unsafe_allow_html=True
)