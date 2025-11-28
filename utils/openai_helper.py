"""
OpenAI API 연동 모듈
"""

import os
import json
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
    """가상 인물 프로필을 생성합니다. 딕셔너리 형태로 반환합니다."""
    try:
        prompt = """당신은 사주 상담소를 방문한 가상의 인물을 생성하는 전문가입니다.
다음 요소를 포함한 인물을 생성해주세요:
- name: 이름 (한국 이름)
- age: 나이 (20-60세 사이의 숫자)
- gender: 성별 ("남성" 또는 "여성")
- occupation: 직업
- personality: 성격 (한 문장으로)
- concern: 현재 고민이나 상황 (구체적으로)
- birth_date: 생년월일 (YYYY-MM-DD 형식)
- birth_time: 출생 시간 (HH:MM 형식)
- speaking_style: 말투 특징

반드시 유효한 JSON 형식으로만 응답하세요. 추가 설명 없이 JSON만 반환하세요."""

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a creative character designer. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        
        # JSON 파싱
        character_data = json.loads(result_text)
        
        return character_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {str(e)}")
        return None
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

def analyze_fortune(character_data: dict, conversation_history: list):
    """
    대화 내용을 분석하여 사주를 해석합니다.
    
    Args:
        character_data: 인물 프로필 딕셔너리
        conversation_history: 대화 기록 리스트 (각 항목은 {"speaker": "user"/"ai", "message": "..."} 형식)
    
    Returns:
        사주 해석 결과 딕셔너리 (fortune_analysis, personality_analysis, advice, summary)
    """
    try:
        # 대화 내용을 문자열로 변환
        conversation_text = "\n".join([
            f"{'손님' if msg['speaker'] == 'user' else character_data['name']}: {msg['message']}"
            for msg in conversation_history
        ])
        
        prompt = f"""당신은 전문 사주 해석가입니다.
다음은 사주를 보러 온 손님과 나눈 대화입니다:

<인물 정보>
이름: {character_data['name']}
나이: {character_data['age']}세
성별: {character_data['gender']}
직업: {character_data['occupation']}
성격: {character_data['personality']}
현재 고민: {character_data['concern']}
생년월일: {character_data['birth_date']}
출생 시간: {character_data['birth_time']}

<대화 내용>
{conversation_text}

위 대화와 인물 정보를 바탕으로 사주를 해석해주세요.
다음 내용을 포함하여 JSON 형식으로 응답하세요:
- fortune_analysis: 전체적인 운세 (4-5문장)
- personality_analysis: 성격 및 성향 분석 (3-4문장)
- advice: 현재 고민에 대한 조언 (3-4문장)
- summary: 한 줄 요약

공감적이고 따뜻한 어조로, 구체적인 조언을 포함해주세요.
전통적인 사주 해석 용어(오행, 천간지지 등)를 적절히 사용하되, 이해하기 쉽게 설명해주세요."""

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional fortune teller specializing in Korean Saju (Four Pillars of Destiny). Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        result_data = json.loads(result_text)
        
        print(f"✅ 사주 해석 완료")
        return result_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 사주 해석 실패: {str(e)}")
        return None

if __name__ == "__main__":
    # Test OpenAI connection
    test_openai_connection()
    
    # Test character generation
    print("\n" + "="*50)
    generate_character_profile()
