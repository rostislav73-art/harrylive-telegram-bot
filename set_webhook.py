
import requests

BOT_TOKEN = "8141162527:AAG0tqiTHkL7GX5jEFwI0F1cnyFqAFqxX3I"

RAILWAY_URL = "https://web-production-f7800.up.railway.app"

# 👉 Генерираме URL за webhook
webhook_url = f"https://web-production-f7800.up.railway.app/bot8141162527:AAG0tqiTHkL7GX5jEfWI0F1cnyFqAFqqx3I"

telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

# 🚀 Изпращаме заявка към Telegram
response = requests.post(telegram_api_url, json={"url": webhook_url})


print("===> Отговор от Telegram:")
print("Статус код:", response.status_code)
print("Съобщение:", response.text)
