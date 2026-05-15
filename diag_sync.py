import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

def test():
    try:
        res = client.models.generate_content(
            model='gemini-1.5-flash',
            contents='hello'
        )
        print(f"Success: {res.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test()
