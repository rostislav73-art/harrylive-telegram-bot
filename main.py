import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://web-production-f7800.up.railway.app/webhook"

client = OpenAI(api_key=OPENAI_API_KEY)


def ask_gpt(message_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти си полезен Telegram бот, който помага на потребителя."},
                {"role": "user", "content": message_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI error:", e)
        return "⚠️ Възникна грешка при връзката с GPT."


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram error:", e)


@app.route("/")
def index():
    return "🤖 Bot is live! Use /webhook for Telegram updates."


@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        reply = ask_gpt(text)
        send_message(chat_id, reply)
    return {"ok": True}


def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    try:
        res = requests.get(url)
        print("Webhook set:", res.json())
    except Exception as e:
        print("Failed to set webhook:", e)


set_webhook()

if __name__ == "__main__":
    app.run(debug=True)
