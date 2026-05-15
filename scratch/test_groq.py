import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("VITE_GROQ_API_KEY"))

try:
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello"}],
        model="llama-3.3-70b-versatile"
    )
    print(chat.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
