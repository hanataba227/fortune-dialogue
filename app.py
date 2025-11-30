"""
사담(四談) - Fortune Dialogue
AI 손님과 대화를 나누며 사주를 풀어가는 감성 대화형 웹 프로젝트
"""

import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv
from datetime import datetime

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.openai_helper import (
    generate_character_profile, chat_with_character, analyze_fortune,
    generate_character_image, download_image
)
from utils.supabase_helper import (
    create_character, create_session, save_message, 
    end_session, get_conversation_history, save_fortune_result,
    get_all_sessions, get_session_detail, upload_image_to_storage,
    update_character_image
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
        animation: fadeIn 0.5s ease-in;
    }
    .user-message {
        background-color: #E8F4F8;
        margin-left: 20%;
    }
    .ai-message {
        background-color: #F5F5DC;
        margin-right: 20%;
        animation: fadeIn 0.5s ease-in, typing 0.8s steps(40) 1;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    .typing-indicator {
        display: inline-block;
        width: 60px;
        text-align: center;
    }
    .typing-indicator span {
        display: inline-block;
        background-color: #8B4513;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin: 0 2px;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    .typing-indicator span:nth-child(1) {
        animation-delay: -0.32s;
    }
    .typing-indicator span:nth-child(2) {
        animation-delay: -0.16s;
    }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
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
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2em;
        }
        .sub-header {
            font-size: 1em;
        }
        .user-message {
            margin-left: 5%;
        }
        .ai-message {
            margin-right: 5%;
        }
        .chat-message {
            padding: 1rem;
        }
        .character-card {
            padding: 1rem;
        }
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
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'new'  # 'new', 'history', 'detail'
if 'selected_session_id' not in st.session_state:
    st.session_state.selected_session_id = None

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
    
    if st.button("📅 상담 기록 보기", use_container_width=True):
        st.session_state.view_mode = 'history'
        st.rerun()
    
    if st.session_state.view_mode == 'history':
        # 과거 상담 목록 표시
        sessions = get_all_sessions(limit=10)
        
        if sessions:
            st.write(f"📊 총 {len(sessions)}건의 상담 기록")
            
            for session in sessions:
                character = session.get('characters', {})
                character_name = character.get('name', '알 수 없음')
                started_at = session.get('started_at', '')
                status = session.get('status', 'unknown')
                
                # 날짜 포맷팅
                if started_at:
                    try:
                        dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = started_at[:16]
                else:
                    date_str = '날짜 없음'
                
                status_emoji = '✅' if status == 'completed' else '🔄'
                
                if st.button(
                    f"{status_emoji} {character_name} ({date_str})",
                    key=f"session_{session['id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_session_id = session['id']
                    st.session_state.view_mode = 'detail'
                    st.rerun()
        else:
            st.info("아직 상담 기록이 없습니다.")
    
    st.divider()
    
    st.subheader("⚙️ 설정")
    st.checkbox("배경 음악", value=False, disabled=True)

# Main content area
if st.session_state.view_mode == 'detail' and st.session_state.selected_session_id:
    # 과거 상담 상세 보기 모드
    session_detail = get_session_detail(st.session_state.selected_session_id)
    
    if session_detail:
        character = session_detail.get('characters', {})
        conversations = session_detail.get('conversations', [])
        fortune_result = session_detail.get('fortune_result')
        
        # 캐릭터 프로필 표시
        with st.container():
            st.markdown('<div class="character-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])
            
            with col1:
                image_url = character.get('image_url')
                if not image_url or image_url == 'None' or image_url.strip() == '':
                    image_url = 'https://via.placeholder.com/150'
                st.image(image_url, caption="인물 이미지")
            
            with col2:
                st.markdown(f"### {character.get('name', '알 수 없음')}")
                st.write(f"**나이**: {character.get('age', '?')}세 | **성별**: {character.get('gender', '?')}")
                st.write(f"**직업**: {character.get('occupation', '?')}")
                st.write(f"**성격**: {character.get('personality', '?')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # 대화 내용 표시
        st.markdown("### 💬 대화 기록")
        
        for conv in conversations:
            speaker = conv.get('speaker')
            message = conv.get('message')
            
            if speaker == 'user':
                st.markdown(f'<div class="chat-message user-message"><strong>나</strong><br>{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message ai-message"><strong>{character.get("name", "AI")}</strong><br>{message}</div>', unsafe_allow_html=True)
        
        # 사주 결과 표시
        if fortune_result:
            st.divider()
            st.markdown('<div class="fortune-title">🔮 사주 해석 결과 🔮</div>', unsafe_allow_html=True)
            
            # Summary card
            st.markdown('''
            <div class="summary-card">
                <div class="fortune-icon">📜</div>
                <div style="font-size: 1.5em; color: #8B4513; font-weight: bold; margin-bottom: 1rem;">운세 요약</div>
                <div class="summary-text">{}</div>
            </div>
            '''.format(fortune_result.get('summary', '운세 요약 없음')), unsafe_allow_html=True)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Detailed analysis
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('''
                <div class="fortune-card" style="background: linear-gradient(135deg, #FFF9E6 0%, #FFFEF5 100%); border-color: #E6C68C;">
                    <div class="fortune-icon">🌟</div>
                    <div class="fortune-section-title">전체 운세</div>
                    <div class="fortune-content">{}</div>
                </div>
                '''.format(fortune_result.get('fortune_analysis', '운세 분석 없음')), unsafe_allow_html=True)
            
            with col2:
                st.markdown('''
                <div class="fortune-card" style="background: linear-gradient(135deg, #F0F8FF 0%, #F8FCFF 100%); border-color: #9BC4E2;">
                    <div class="fortune-icon">💎</div>
                    <div class="fortune-section-title">성격 및 성향</div>
                    <div class="fortune-content">{}</div>
                </div>
                '''.format(fortune_result.get('personality_analysis', '성격 분석 없음')), unsafe_allow_html=True)
            
            with col3:
                st.markdown('''
                <div class="fortune-card" style="background: linear-gradient(135deg, #FFF5F0 0%, #FFFAF8 100%); border-color: #E6B09B;">
                    <div class="fortune-icon">💡</div>
                    <div class="fortune-section-title">조언</div>
                    <div class="fortune-content">{}</div>
                </div>
                '''.format(fortune_result.get('advice', '조언 없음')), unsafe_allow_html=True)
    else:
        st.error("세션 정보를 불러올 수 없습니다.")
    
elif st.session_state.character is None and st.session_state.view_mode == 'new':
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
                        # Generate character image (optional - don't fail if it doesn't work)
                        with st.spinner("인물 이미지를 생성하고 있습니다..."):
                            try:
                                image_url = generate_character_image(character_data)
                                
                                if image_url:
                                    # Download image
                                    image_data = download_image(image_url)
                                    
                                    if image_data:
                                        # Upload to Supabase Storage
                                        storage_url = upload_image_to_storage(image_data, character_id)
                                        
                                        if storage_url:
                                            # Update character image URL in database
                                            update_character_image(character_id, storage_url)
                                            character_data['image_url'] = storage_url
                                        else:
                                            character_data['image_url'] = image_url  # Use temporary URL
                            except Exception as e:
                                print(f"⚠️ 이미지 생성 실패 (계속 진행): {str(e)}")
                                character_data['image_url'] = None
                        
                        # Create session
                        session_id = create_session(character_id)
                        
                        if session_id:
                            st.session_state.character = character_data
                            st.session_state.character_id = character_id
                            st.session_state.session_id = session_id
                            st.session_state.view_mode = 'new'
                            
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
elif st.session_state.character is not None and st.session_state.view_mode == 'new':
    # Character profile display
    with st.container():
        st.markdown('<div class="character-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        
        with col1:
            image_url = st.session_state.character.get('image_url')
            if not image_url or image_url == 'None' or str(image_url).strip() == '':
                image_url = 'https://via.placeholder.com/150'
            st.image(image_url, caption="인물 이미지")
        
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
        # Show typing indicator
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            f'<div class="chat-message ai-message"><strong>{st.session_state.character["name"]}</strong><br/><div class="typing-indicator"><span></span><span></span><span></span></div></div>',
            unsafe_allow_html=True
        )
        
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
        
        # Clear typing indicator
        typing_placeholder.empty()
        
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