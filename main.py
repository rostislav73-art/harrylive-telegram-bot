import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv
import openai

# Зареждане на .env променливите
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAILWAY_STATIC_URL = os.getenv("RAILWAY_STATIC_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ BOT_TOKEN или OPENAI_API_KEY не са зададени като среда (environment variables)")

openai.api_key = OPENAI_API_KEY

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Настройка на webhook
webhook_url = f"{RAILWAY_STATIC_URL}/{BOT_TOKEN}"
bot.remove_webhook()
bot.set_webhook(url=webhook_url)
print("✅ Webhook set to:", webhook_url)

# Handler за /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "👋 Здрасти! Аз съм HarryLiveBot_73 — готов съм да говоря с теб!")

# Echo handler – изпраща към GPT-4 Turbo
@bot.message_handler(func=lambda message: True)
def echo(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Ти си помощник в Telegram и отговаряш учтиво и ясно."},
                {"role": "user", "content": message.text}
            ]
        )
        gpt_reply = response['choices'][0]['message']['content']
        bot.send_message(message.chat.id, gpt_reply)
    except Exception as e:
        print("⚠️ GPT Error:", e)
        bot.send_message(message.chat.id, "❌ Възникна грешка при връзката с GPT.")

# Webhook endpoint – получава съобщения от Telegram
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

# Проверка дали Flask работи
@app.route("/", methods=["GET"])
def index():
    return "✅ HarryLive Telegram Bot is running!", 200

# Стартиране на Flask
if __name__ == "__main__" or os.environ.get("RAILWAY_STATIC_URL"):
    print("🚀 Starting Flask app...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
