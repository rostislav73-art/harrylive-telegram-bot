import os
import requests
import openai
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# ✅ Разрешени потребители (само тези chat_id ще получават отговор)
ALLOWED_USERS = [6255661181]  # смени с твоя chat_id

@app.route("/")
def home():
    return "Bot is live!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📥 Telegram update:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # 🔒 Блокирай непознати потребители
        if chat_id not in ALLOWED_USERS:
            print(f"❌ Blocked user {chat_id}")
            return {"ok": True}

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": text}]
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            print("OpenAI error:", e)
            reply = "⚠️ OpenAI error"

        payload = {"chat_id": chat_id, "text": reply}
        headers = {"Content-Type": "application/json"}
        r = requests.post(API_URL, json=payload, headers=headers)
        print("📤 Telegram response:", r.status_code, r.text)

    return {"ok": True"}
