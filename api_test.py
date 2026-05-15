
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GOOGLE_API_KEY')

print(f"Testing API Key: {api_key[:10]}...")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents="Hi"
    )
    print("SUCCESS: API Key is working!")
    print(f"Response: {response.text}")
except Exception as e:
    print("\nFAILURE: API Key test failed.")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
