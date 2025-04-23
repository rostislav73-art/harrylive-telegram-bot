import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": "Hello, GPT-4 Turbo?"}]
    )
    print("✅ Успешно:", response.choices[0].message.content)
except Exception as e:
    print("❌ Грешка:", e)
