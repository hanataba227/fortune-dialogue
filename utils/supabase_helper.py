"""
Supabase Database Helper
데이터베이스 저장 및 조회 기능
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Supabase 클라이언트를 반환합니다."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다.")
    
    return create_client(url, key)

def create_character(character_data: dict) -> str:
    """
    새로운 인물을 데이터베이스에 저장합니다.
    
    Args:
        character_data: 인물 정보 딕셔너리
        
    Returns:
        생성된 인물의 UUID
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "name": character_data.get("name"),
            "age": character_data.get("age"),
            "gender": character_data.get("gender"),
            "occupation": character_data.get("occupation"),
            "personality": character_data.get("personality"),
            "background_story": character_data.get("concern"),
            "birth_date": character_data.get("birth_date"),
            "birth_time": character_data.get("birth_time"),
            "speaking_style": character_data.get("speaking_style"),
            "image_url": character_data.get("image_url")
        }
        
        result = supabase.table("characters").insert(data).execute()
        character_id = result.data[0]["id"]
        print(f"✅ 인물 저장 완료: {character_id}")
        return character_id
        
    except Exception as e:
        print(f"❌ 인물 저장 실패: {str(e)}")
        return None

def create_session(character_id: str, user_id: str = "anonymous") -> str:
    """
    새로운 상담 세션을 생성합니다.
    
    Args:
        character_id: 인물 UUID
        user_id: 사용자 ID (기본값: "anonymous")
        
    Returns:
        생성된 세션의 UUID
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "character_id": character_id,
            "user_id": user_id,
            "status": "active"
        }
        
        result = supabase.table("sessions").insert(data).execute()
        session_id = result.data[0]["id"]
        print(f"✅ 세션 생성 완료: {session_id}")
        return session_id
        
    except Exception as e:
        print(f"❌ 세션 생성 실패: {str(e)}")
        return None

def save_message(session_id: str, character_id: str, speaker: str, message: str) -> bool:
    """
    대화 메시지를 저장합니다.
    
    Args:
        session_id: 세션 UUID
        character_id: 인물 UUID
        speaker: 'user' 또는 'ai'
        message: 메시지 내용
        
    Returns:
        저장 성공 여부
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "session_id": session_id,
            "character_id": character_id,
            "speaker": speaker,
            "message": message
        }
        
        supabase.table("conversations").insert(data).execute()
        return True
        
    except Exception as e:
        print(f"❌ 메시지 저장 실패: {str(e)}")
        return False

def get_conversation_history(session_id: str) -> list:
    """
    세션의 대화 기록을 가져옵니다.
    
    Args:
        session_id: 세션 UUID
        
    Returns:
        대화 기록 리스트
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("conversations")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("timestamp")\
            .execute()
        
        return result.data
        
    except Exception as e:
        print(f"❌ 대화 기록 조회 실패: {str(e)}")
        return []

def end_session(session_id: str) -> bool:
    """
    세션을 종료합니다.
    
    Args:
        session_id: 세션 UUID
        
    Returns:
        종료 성공 여부
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "status": "completed",
            "ended_at": datetime.now().isoformat()
        }
        
        supabase.table("sessions")\
            .update(data)\
            .eq("id", session_id)\
            .execute()
        
        print(f"✅ 세션 종료 완료: {session_id}")
        return True
        
    except Exception as e:
        print(f"❌ 세션 종료 실패: {str(e)}")
        return False

def save_fortune_result(session_id: str, character_id: str, result_data: dict) -> bool:
    """
    사주 해석 결과를 저장합니다.
    
    Args:
        session_id: 세션 UUID
        character_id: 인물 UUID
        result_data: 해석 결과 딕셔너리
        
    Returns:
        저장 성공 여부
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "session_id": session_id,
            "character_id": character_id,
            "fortune_analysis": result_data.get("fortune_analysis"),
            "personality_analysis": result_data.get("personality_analysis"),
            "advice": result_data.get("advice"),
            "summary": result_data.get("summary")
        }
        
        supabase.table("fortune_results").insert(data).execute()
        print(f"✅ 사주 결과 저장 완료")
        return True
        
    except Exception as e:
        print(f"❌ 사주 결과 저장 실패: {str(e)}")
        return False

def get_all_sessions(limit: int = 10) -> list:
    """
    최근 세션 목록을 가져옵니다.
    
    Args:
        limit: 가져올 세션 수
        
    Returns:
        세션 리스트
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("sessions")\
            .select("*, characters(name, age, occupation)")\
            .order("started_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data
        
    except Exception as e:
        print(f"❌ 세션 목록 조회 실패: {str(e)}")
        return []

if __name__ == "__main__":
    # Test database connection
    print("🔄 데이터베이스 연결 테스트 중...")
    
    try:
        supabase = get_supabase_client()
        result = supabase.table("characters").select("count").execute()
        print("✅ 데이터베이스 연결 성공!")
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {str(e)}")
