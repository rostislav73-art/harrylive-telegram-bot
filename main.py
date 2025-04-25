from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")


@app.route("/")
def index():
    return "🤖 Bot is live! Use /webhook for Telegram updates."


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    # Тук обработваш съобщенията от Telegram
    print("Received:", data)
    return {"status": "ok"}


@app.before_first_request
def set_webhook():
    webhook_url = "https://web-production-f7800.up.railway.app/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        r = requests.get(url)
        print("Webhook set:", r.json())
    except Exception as e:
        print("Failed to set webhook:", e)


if __name__ == "__main__":
    app.run(debug=True)
