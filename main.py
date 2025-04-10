import os
import telebot
import openai

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am Harry live Bot73 and I'm online.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if OPENAI_API_KEY:
        try:
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message.text}
                ]
            )
            reply = response.choices[0].message.content
            bot.reply_to(message, reply)
        except Exception:
            bot.reply_to(message, "I'm here, but can't reach OpenAI right now.")
    else:
        bot.reply_to(message, message.text)

print("Bot is running...")
bot.infinity_polling()