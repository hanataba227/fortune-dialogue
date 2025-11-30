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

def get_all_sessions(limit: int = 10, user_id: str = "anonymous") -> list:
    """
    최근 세션 목록을 가져옵니다.
    
    Args:
        limit: 가져올 세션 수
        user_id: 사용자 ID (기본값: "anonymous")
        
    Returns:
        세션 리스트 (인물 정보 포함)
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("sessions")\
            .select("*, characters(name, age, gender, occupation)")\
            .eq("user_id", user_id)\
            .order("started_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
        
        return result.data
        
    except Exception as e:
        print(f"❌ 세션 목록 조회 실패: {str(e)}")
        return []

def get_session_detail(session_id: str) -> dict:
    """
    특정 세션의 상세 정보를 가져옵니다.
    
    Args:
        session_id: 세션 UUID
        
    Returns:
        세션 상세 정보 (인물, 대화, 사주 결과 포함)
    """
    try:
        supabase = get_supabase_client()
        
        # 세션 기본 정보 조회
        session_result = supabase.table("sessions")\
            .select("*, characters(*)")\
            .eq("id", session_id)\
            .execute()
        
        if not session_result.data or len(session_result.data) == 0:
            return None
        
        session_data = session_result.data[0]
        
        # 대화 내역 조회
        conversations = get_conversation_history(session_id)
        session_data["conversations"] = conversations
        
        # 사주 결과 조회
        fortune_result = supabase.table("fortune_results")\
            .select("*")\
            .eq("session_id", session_id)\
            .execute()
        
        if fortune_result.data:
            session_data["fortune_result"] = fortune_result.data[0]
        else:
            session_data["fortune_result"] = None
        
        return session_data
        
    except Exception as e:
        print(f"❌ 세션 상세 조회 실패: {str(e)}")
        return None

def get_fortune_result_by_session(session_id: str) -> dict:
    """
    특정 세션의 사주 해석 결과를 가져옵니다.
    
    Args:
        session_id: 세션 UUID
        
    Returns:
        사주 해석 결과 딕셔너리
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("fortune_results")\
            .select("*")\
            .eq("session_id", session_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
        
    except Exception as e:
        print(f"❌ 사주 결과 조회 실패: {str(e)}")
        return None

def upload_image_to_storage(image_data: bytes, character_id: str) -> str:
    """
    이미지를 Supabase Storage에 업로드합니다.
    
    Args:
        image_data: 이미지 바이트 데이터
        character_id: 인물 UUID (파일명으로 사용)
        
    Returns:
        업로드된 이미지의 공개 URL
    """
    try:
        if not image_data:
            print("❌ 이미지 데이터가 없습니다.")
            return None
            
        supabase = get_supabase_client()
        
        # 파일명 생성 (타임스탬프 추가하여 중복 방지)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"characters/{character_id}_{timestamp}.png"
        
        print(f"🔄 이미지 업로드 시도: {file_name}")
        
        # Storage에 업로드
        try:
            # 기존 파일이 있으면 먼저 삭제 시도
            supabase.storage.from_("character-images").remove([file_name])
        except:
            pass  # 파일이 없으면 무시
        
        # 업로드
        upload_result = supabase.storage.from_("character-images").upload(
            path=file_name,
            file=image_data,
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        
        # 공개 URL 생성
        public_url = supabase.storage.from_("character-images").get_public_url(file_name)
        
        print(f"✅ 이미지 업로드 완료: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ 이미지 업로드 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def update_character_image(character_id: str, image_url: str) -> bool:
    """
    인물의 이미지 URL을 업데이트합니다.
    
    Args:
        character_id: 인물 UUID
        image_url: 이미지 URL
        
    Returns:
        업데이트 성공 여부
    """
    try:
        supabase = get_supabase_client()
        
        supabase.table("characters")\
            .update({"image_url": image_url})\
            .eq("id", character_id)\
            .execute()
        
        print(f"✅ 인물 이미지 URL 업데이트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 이미지 URL 업데이트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    # Test database connection
    print("🔄 데이터베이스 연결 테스트 중...")
    
    try:
        supabase = get_supabase_client()
        result = supabase.table("characters").select("count").execute()
        print("✅ 데이터베이스 연결 성공!")
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {str(e)}")
