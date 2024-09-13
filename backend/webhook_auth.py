from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging

TOKEN = '7304038568:AAHrDrL4u7k7d6oIfdLiThSEgVgKnyFKXU4'
#ngrok_url = 'https://stattron.ru/telegram_auth/'  # Replace with your NGROK URL
ngrok_url = 'https://b0dd-5-133-120-92.ngrok-free.app/telegram_auth/'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())
#daphne -p 8000 Statron.asgi:application



async def set_webhook(dispatcher):
    try:
        webhook_url = f"{ngrok_url}"
        await bot.set_webhook(webhook_url)
        logging.info(f"Webhook set to {webhook_url}")
    except Exception as e:
        logging.error(f"Failed to set webhook: {e}")

# Add other handlers here

if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path='/telegram_auth/',
        on_startup=set_webhook,
        skip_updates=True,
        host='0.0.0.0',
        port=6000,
    )
