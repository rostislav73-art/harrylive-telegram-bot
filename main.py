import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://web-production-f7800.up.railway.app/webhook"

# Сетваме webhook още при стартиране
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    try:
        res = requests.get(url)
        print("Webhook set:", res.json())
    except Exception as e:
        print("Failed to set webhook:", e)

set_webhook()  # извикваме го веднага


@app.route("/")
def index():
    return "🤖 Bot is live! Use /webhook for Telegram updates."


@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        reply = f"Echo: {text}"
        send_message(chat_id, reply)
    return {"ok": True}


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


if __name__ == "__main__":
    app.run(debug=True)
