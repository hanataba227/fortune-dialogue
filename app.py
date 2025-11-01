from dotenv import load_dotenv
import os

# dotenv 라이브러리를 가지고 오기
load_dotenv()

# .env 파일에서 OPENAI_API_KEY 값을 가져오기
openai_api_key = os.getenv("OPENAI_API_KEY")

print(f"Your OpenAI API Key: {openai_api_key}")