import os
from flask import Flask, request
from dotenv import load_dotenv
import telebot
import openai

# Зареждаме променливите от .env файла или от средата
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RAILWAY_STATIC_URL = os.getenv("RAILWAY_STATIC_URL")
PORT = int(os.getenv("PORT", 8000))

# Настройка на OpenAI
openai.api_key = OPENAI_API_KEY

# Създаване на Telegram бот
bot = telebot.TeleBot(BOT_TOKEN)

# Flask приложение
app = Flask(__name__)

# Рут за health check
@app.route("/", methods=["GET"])
def index():
    return "✅ HarryLiveBot работи!"

# Рут за webhook (приема съобщения от Telegram)
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Здрасти! Аз съм HarryLiveBot_73 и съм тук да ти помагам с GPT-4.")

# Отговор на всяко текстово съобщение
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_input}
            ]
        )

        reply = response.choices[0]['message']['content']
    except Exception as e:
        reply = f"❌ Грешка при връзка с OpenAI: {str(e)}"

    bot.reply_to(message, reply)

# Стартиране на Flask приложението + задаване на webhook
if __name__ == "__main__":
    webhook_url = f"{RAILWAY_STATIC_URL}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook зададен към: {webhook_url}")

    app.run(host="0.0.0.0", port=PORT)
