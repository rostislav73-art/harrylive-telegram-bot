import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv

# Зареждане на .env променливите
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAILWAY_STATIC_URL = os.getenv("RAILWAY_STATIC_URL")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in environment variables")

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
    bot.send_message(message.chat.id, "👋 Здрасти! Аз съм HarryLiveBot_73 – готов съм да говоря с теб!")

# Echo handler – повтаря всичко
@bot.message_handler(func=lambda message: True)
def echo(message):
    try:
        bot.send_message(message.chat.id, message.text)
    except Exception as e:
        print("⚠️ Error:", e)

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

# Стартиране на Flask и локално, и в Railway
if __name__ == "__main__":
    print("🚀 Running Flask locally...")
    app.run(host="0.0.0.0", port=5000)

