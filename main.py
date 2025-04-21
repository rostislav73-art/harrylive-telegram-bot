import os
import openai
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Зареждане на .env файла
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

app = Flask(__name__)

# Новият метод за Chat Completion
def generate_reply(message_text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message_text}
        ]
    )
    return response.choices[0].message.content

# Проверка дали приложението работи
@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📥 Incoming:", data)

    try:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        reply = generate_reply(text)

        payload = {
            "chat_id": chat_id,
            "text": reply
        }

        r = requests.post(API_URL, json=payload)
        print("📤 Sent:", r.status_code, r.text)

    except Exception as e:
        print("❌ Error:", e)

    return {"ok": True}
