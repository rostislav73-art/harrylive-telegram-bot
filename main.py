import os
import requests
import openai
from flask import Flask, request
from dotenv import load_dotenv

# Зареждаме .env
load_dotenv()

# Четем ключовете
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ✅ Дебъг принтове
print("✅ BOT_TOKEN:", BOT_TOKEN)
print("✅ API_URL:", API_URL)

# Настройка на OpenAI
openai.api_key = OPENAI_API_KEY

# Flask приложение
app = Flask(__name__)

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

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": text}]
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            print("🔴 OpenAI error:", e)
            reply = "⚠️ OpenAI error"

        payload = {"chat_id": chat_id, "text": reply}
        headers = {"Content-Type": "application/json"}
        r = requests.post(API_URL, json=payload, headers=headers)
        print("📤 Telegram response:", r.status_code, r.text)

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
