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

from utils.openai_helper import generate_character_profile, chat_with_character, analyze_fortune
from utils.supabase_helper import (
    create_character, create_session, save_message, 
    end_session, get_conversation_history, save_fortune_result
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
    
    /* 사주 결과 전용 스타일 */
    .fortune-title {
        text-align: center;
        color: #8B4513;
        font-size: 2.5em;
        font-weight: bold;
        margin: 2rem 0 1.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .fortune-card {
        background: linear-gradient(135deg, #FFF8F0 0%, #FFFAF5 100%);
        padding: 2rem;
        border-radius: 1.5rem;
        border: 3px solid #D4A574;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 16px rgba(139, 69, 19, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .fortune-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(139, 69, 19, 0.25);
    }
    
    .summary-card {
        background: linear-gradient(135deg, #FFE5D0 0%, #FFF0E5 100%);
        padding: 2.5rem;
        border-radius: 2rem;
        border: 4px solid #C8956E;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(139, 69, 19, 0.2);
        text-align: center;
    }
    
    .fortune-section-title {
        color: #8B4513;
        font-size: 1.4em;
        font-weight: bold;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #D4A574;
    }
    
    .fortune-content {
        color: #4A4A4A;
        font-size: 1.05em;
        line-height: 1.8;
        text-align: justify;
    }
    
    .summary-text {
        color: #8B4513;
        font-size: 1.3em;
        font-weight: 600;
        line-height: 1.6;
    }
    
    .fortune-icon {
        font-size: 2em;
        margin-bottom: 0.5rem;
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
if 'fortune_result' not in st.session_state:
    st.session_state.fortune_result = None
if 'consultation_ended' not in st.session_state:
    st.session_state.consultation_ended = False

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
        st.session_state.fortune_result = None
        st.session_state.consultation_ended = False
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
    
    # End consultation button (only show if consultation not ended)
    if not st.session_state.consultation_ended:
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔮 상담 종료 및 사주 결과 보기", use_container_width=True):
                if len(st.session_state.messages) > 2:  # At least some conversation happened
                    # First, mark the session as ended in the database so status reflects user's action
                    with st.spinner("상담을 종료 처리하고 있습니다..."):
                        ended = end_session(st.session_state.session_id)

                    if not ended:
                        st.warning("세션 상태를 데이터베이스에 업데이트하지 못했습니다. 계속해서 결과 생성을 시도합니다.")

                    # Show a new spinner while analyzing and saving the result
                    with st.spinner("대화 내용을 분석하고 사주를 해석하고 있습니다..."):
                        # Get conversation history from database
                        db_messages = get_conversation_history(st.session_state.session_id)

                        # Convert to format needed for analysis
                        conversation_for_analysis = [
                            {"speaker": msg["speaker"], "message": msg["message"]}
                            for msg in db_messages
                        ]

                        # Analyze fortune
                        fortune_result = analyze_fortune(
                            st.session_state.character,
                            conversation_for_analysis
                        )

                        if fortune_result:
                            # Try to save fortune result to database
                            save_success = save_fortune_result(
                                st.session_state.session_id,
                                st.session_state.character_id,
                                fortune_result
                            )

                            # Update session state regardless of save success (session already ended)
                            st.session_state.fortune_result = fortune_result
                            st.session_state.consultation_ended = True

                            if save_success:
                                st.success("✨ 사주 해석이 완료되었습니다! 결과가 저장되었습니다.")
                            else:
                                st.error("사주 해석은 완료되었지만, 결과 저장에 실패했습니다. 로그를 확인해주세요.")

                            # Rerun to show results (or partial state)
                            st.rerun()
                        else:
                            # Analysis failed, but session is ended
                            st.session_state.consultation_ended = True
                            st.error("사주 해석에 실패했습니다. 세션은 종료되었습니다.")
                            st.rerun()
                else:
                    st.warning("대화를 더 나눈 후에 상담을 종료해주세요.")
    
    # Display fortune result if consultation ended
    if st.session_state.consultation_ended and st.session_state.fortune_result:
        st.divider()
        
        # Fortune result title with traditional style
        st.markdown('<div class="fortune-title">🔮 사주 해석 결과 🔮</div>', unsafe_allow_html=True)
        
        result = st.session_state.fortune_result
        
        # Summary card - prominent display
        st.markdown('''
        <div class="summary-card">
            <div class="fortune-icon">📜</div>
            <div style="font-size: 1.5em; color: #8B4513; font-weight: bold; margin-bottom: 1rem;">운세 요약</div>
            <div class="summary-text">{}</div>
        </div>
        '''.format(result.get('summary', '운세 요약 없음')), unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Detailed analysis in three columns for better readability
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('''
            <div class="fortune-card" style="background: linear-gradient(135deg, #FFF9E6 0%, #FFFEF5 100%); border-color: #E6C68C;">
                <div class="fortune-icon">🌟</div>
                <div class="fortune-section-title">전체 운세</div>
                <div class="fortune-content">{}</div>
            </div>
            '''.format(result.get('fortune_analysis', '운세 분석 없음')), unsafe_allow_html=True)
        
        with col2:
            st.markdown('''
            <div class="fortune-card" style="background: linear-gradient(135deg, #F0F8FF 0%, #F8FCFF 100%); border-color: #9BC4E2;">
                <div class="fortune-icon">💎</div>
                <div class="fortune-section-title">성격 및 성향</div>
                <div class="fortune-content">{}</div>
            </div>
            '''.format(result.get('personality_analysis', '성격 분석 없음')), unsafe_allow_html=True)
        
        with col3:
            st.markdown('''
            <div class="fortune-card" style="background: linear-gradient(135deg, #FFF5F0 0%, #FFFAF8 100%); border-color: #E6B09B;">
                <div class="fortune-icon">💡</div>
                <div class="fortune-section-title">조언</div>
                <div class="fortune-content">{}</div>
            </div>
            '''.format(result.get('advice', '조언 없음')), unsafe_allow_html=True)
        
        # Additional decorative element
        st.markdown("<div style='text-align: center; margin-top: 2rem; color: #A0826D; font-size: 1.1em;'>🪶 상담이 완료되었습니다 🪶</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888; font-size: 0.9em;">사담(四談) - Fortune Dialogue | Powered by OpenAI & Supabase</div>',
    unsafe_allow_html=True
)