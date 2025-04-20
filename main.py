from flask import Flask, request
import requests
import os
import openai

app = Flask(__name__)

# 🔐 Зареждане на ключове от средата
bot_token = os.getenv("BOT_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

# 🧠 Настройка на OpenAI API ключ
openai.api_key = openai_api_key

# 📩 Telegram Webhook логика
@app.route(f"/{bot_token}", methods=["POST"])
def telegram_webhook():
    data = request.json

    # 🔍 Проверка дали съобщението е валидно
    if "message" not in data or "text" not in data["message"]:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    user_message = data["message"]["text"]

    try:
        # 🧠 Изпращане на заявка към OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print("OpenAI Error:", e)
        reply = "⚠️ Възникна грешка при отговора от GPT."

    # 📤 Изпращане на отговора обратно към Telegram
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(telegram_url, json={"chat_id": chat_id, "text": reply})

    return {"ok": True}

# 🌐 Проверка за статус
@app.route("/")
def home():
    return "Bot is running!"

# 🚀 Flask стартиране – Railway задава порта автоматично
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
