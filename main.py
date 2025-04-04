import os
import telebot
import openai

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
openai.api_key = os.getenv("OPENAI_KEY")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.text}]
    )
    reply = response.choices[0].message.content
    bot.send_message(message.chat.id, reply)

bot.polling()
