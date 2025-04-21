import os
import openai
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Зареждане на .env
load_dotenv()

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
openai.api_key = OPENAI_API_KEY

print("🤖 BOT_TOKEN:", BOT_TOKEN[:10], "...")  # частично логване
print("🧠 OPENAI_API_KEY:", OPENAI_API_KEY[:10], "...")

# Flask
app = Flask(__name__)

# Генериране на отговор от OpenAI
def generate_reply(message_text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message_text}
        ]
    )
    return response.choices[0].message.content

# Проверка дали работи
@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        print("✅ Получени данни:", data)
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        print("📩 Получен текст:", text)

        reply = generate_reply(text)
        print("🤖 Генериран отговор:", reply)

        payload = {
            "chat_id": chat_id,
            "text": reply
        }

        response = requests.post(API_URL, json=payload)
        print("📬 Telegram API статус:", response.status_code)
        print("📨 Telegram API отговор:", response.text)

    except Exception as e:
        print("❌ Грешка:", e)

    return {"ok": True}
