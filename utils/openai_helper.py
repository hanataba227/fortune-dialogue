"""
OpenAI API 연동 모듈
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get GPT model from environment variable
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")

def test_openai_connection():
    """OpenAI API 연결을 테스트합니다."""
    try:
        print("🔄 OpenAI API 연결 테스트 중...")
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "안녕하세요. 간단히 인사해주세요."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API 연결 성공!")
        print(f"   응답: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API 연결 실패: {str(e)}")
        return False

def generate_character_profile():
    """가상 인물 프로필을 생성합니다."""
    try:
        print("\n🎭 인물 프로필 생성 중...")
        
        prompt = """당신은 사주 상담소를 방문한 가상의 인물을 생성하는 전문가입니다.
다음 요소를 포함한 인물을 생성해주세요:
- 이름 (한국 이름)
- 나이 (20-60세)
- 성별
- 직업
- 성격 (3-4가지 특징)
- 현재 고민이나 상황
- 생년월일시 (음력 가능, 형식: YYYY-MM-DD HH:MM)
- 말투 특징

자연스럽고 공감 가능한 인물을 만들어주세요.
JSON 형식으로 응답해주세요."""

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a creative character designer for fortune-telling consultations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        print(f"✅ 인물 프로필 생성 완료!")
        print(f"\n{result}")
        return result
        
    except Exception as e:
        print(f"❌ 인물 프로필 생성 실패: {str(e)}")
        return None

def chat_with_character(character_context: str, user_message: str, conversation_history: list = None):
    """인물과 대화를 진행합니다."""
    try:
        if conversation_history is None:
            conversation_history = []
        
        messages = [
            {"role": "system", "content": f"당신은 다음과 같은 인물입니다:\n{character_context}\n\n사주를 보러 온 손님으로서 자연스럽게 대화하세요."}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ 대화 생성 실패: {str(e)}")
        return None

if __name__ == "__main__":
    # Test OpenAI connection
    test_openai_connection()
    
    # Test character generation
    print("\n" + "="*50)
    generate_character_profile()
