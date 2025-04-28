@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chat_id = message.chat.id
    text = message.text.strip()

    known_commands = ["/start", "/help", "/weather", "/chatgpt", "/setwebhook"]

    if text.startswith("/"):
        if text.lower() not in known_commands:
            bot.send_message(chat_id, f"❓ *Неразпозната команда:* `{text}`\n\n*Използвай /start за менюто!*")
            return

    context = user_context.get(chat_id, [])

    if context and context[0]["content"] == "awaiting_city":
        bot.send_chat_action(chat_id, 'typing')
        reply = get_weather(text)
        bot.send_message(chat_id, reply)
        user_context[chat_id] = []
        return

    lowered = text.lower()

    if "времето в" in lowered:
        try:
            bot.send_chat_action(chat_id, 'typing')
            city = lowered.split("времето в", 1)[1].strip().rstrip("?.,!")
            reply = get_weather(city)
            bot.send_message(chat_id, reply)
        except Exception as e:
            print("City parse error:", e)
            bot.send_message(chat_id, "⚠️ *Моля, задай въпроса отново по правилен начин!*")
        return

    if lowered.startswith(("кой е", "какво е", "кога е", "къде е", "who is", "what is", "when is", "where is")):
        bot.send_chat_action(chat_id, 'typing')
        wiki_info = search_wikipedia(text, chat_id)
        if wiki_info:
            bot.send_message(chat_id, wiki_info)
            return

    if "хари" in lowered:
        bot.send_chat_action(chat_id, 'typing')
        if "какво правиш" in lowered:
            bot.send_message(chat_id, "🤖 Работя неуморно, за да ти помагам! Какво ще пожелаеш?")
        elif "къде си" in lowered:
            bot.send_message(chat_id, "📍 В дигиталния свят съм, винаги до теб! Какво мога да направя?")
        elif "кой си" in lowered:
            bot.send_message(chat_id, "👋 Аз съм Хари — твоят Telegram помощник, свързан с GPT-4! 🚀")
        else:
            bot.send_message(chat_id, "👋 Здравей! Какво мога да направя за теб?")
        return

    bot.send_chat_action(chat_id, 'typing')
    reply = ask_gpt(chat_id, text)
    bot.send_message(chat_id, reply)
