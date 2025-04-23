import os
import requests
import openai
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# 👥 Разрешени потребители
ALLOWED_USERS = [6255661181]  # замени с твоя chat_id

@app.route("/")
def home():
    return "Bot is live!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Telegram update:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        print(f"📥 Получено: [{chat_id}] {text}")

        # 🔒 Блокирай неразрешени потребители
        if chat_id not in ALLOWED_USERS:
            print(f"❌ Блокиран: {chat_id}")
            return {"ok": True}

        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": text}]
            )
            reply = response.choices[0].message.content.strip()
            print(f"🤖 Отговор от GPT: {reply}")
        except Exception as e:
            print("❌ OpenAI error:", e)
            reply = "⚠️ OpenAI грешка"

        # 📝 Запис в лог файл
        with open("logs.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] [{chat_id}] {text} → {reply}\n")

        # 📤 Изпращане обратно към Telegram
        payload = {"chat_id": chat_id, "text": reply}
        headers = {"Content-Type": "application/json"}
        r = requests.post(API_URL, json=payload, headers=headers)
        print("✅ Telegram статус:", r.status_code, r.text)

    return {"ok": True}
