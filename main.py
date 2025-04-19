import os
from flask import Flask, request
import telebot
from openai import OpenAI
from dotenv import load_dotenv

# Зареждане на .env променливите
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAILWAY_STATIC_URL = os.getenv("RAILWAY_STATIC_URL")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in environment variables")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY is not set in environment variables")

# Инициализация на Telebot и Flask
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Задаваме OpenAI API ключ
os.environ["OPENAI_API_KEY"] = openai_api_key
client = OpenAI()

# Настройка на webhook
webhook_url = f"{RAILWAY_STATIC_URL}/{BOT_TOKEN}"
bot.remove_webhook()
bot.set_webhook(url=webhook_url)
print("✅ Webhook set to:", webhook_url)

# /start handler
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "👋 Здрасти! Аз съм HarryLiveBot_73 – готов съм да говоря с теб!")

# GPT handler
@bot.message_handler(func=lambda message: True)
def gpt_handler(message):
    try:
        user_input = message.text
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Ти си полезен асистент в Telegram."},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
        bot.send_message(message.chat.id, reply)

    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Възникна грешка при отговора от GPT.")
        print("❌ Error:", e)

# Webhook endpoint – получава съобщения от Telegram
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

# Статус проверка
@app.route("/", methods=["GET"])
def index():
    return "✅ HarryLive Telegram Bot is running!", 200

# Flask сървър
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
