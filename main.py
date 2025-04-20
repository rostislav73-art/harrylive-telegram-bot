from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

# 🗝️ Зареждане на API ключовете от .env или среда
bot_token = os.getenv("BOT_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

# 🧠 Създаване на OpenAI клиент
client = OpenAI(api_key=openai_api_key)

# 📬 Основна логика: получава съобщения от Telegram
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.json

    if "message" not in data or "text" not in data["message"]:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    user_message = data["message"]["text"]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print("⚠️ OpenAI Error:", e)
        reply = "⚠️ Възникна грешка при обработка на отговора."

    # 📤 Изпращане обратно към Telegram
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(telegram_url, json={"chat_id": chat_id, "text": reply})

    return {"ok": True}

# ✅ Проверка за статус
@app.route("/")
def home():
    return "Bot is running!"

# 🚀 Стартиране за Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
