import requests

BOT_TOKEN = "8141162527:AAHLjr6MbQPx2RlgQKdOavFMSQOMPnQB8xo".strip()
RAILWAY_URL = "https://web-production-f7800.up.railway.app"

# Генериране URL за webhook
webhook_url = f"{RAILWAY_URL}/webhook"
telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

# Изпращане заявка към Telegram
response = requests.post(telegram_api_url, json={"url": webhook_url})

print("==> Отговор от Telegram:")
print("Статус код:", response.status_code)
print("Съобщение:", response.text)
