import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

try:
    response = client.models.list()
    print("✅ OpenAI API ключът е валиден.")
except Exception as e:
    print("❌ Грешка при свързване с OpenAI:", e)
