import os
import telebot
import openai
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

    @bot.message_handler(func=lambda message: True)
    def chat_with_gpt(message):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message.text}
                ]
            )
            reply = response.choices[0].message.content
            bot.reply_to(message, reply)
        except Exception as e:
            bot.reply_to(message, f"Грешка от OpenAI: {e}")
else:
    @bot.message_handler(func=lambda message: True)
    def echo(message):
        bot.reply_to(message, message.text)

print("Bot is running...")
bot.infinity_polling()
