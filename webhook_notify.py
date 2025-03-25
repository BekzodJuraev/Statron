from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging
from config import TOKEN_NOTIFY


#ngrok_url = 'https://stattron.ru/telegram_auth/'  # Replace with your NGROK URL
ngrok_url = 'https://stattron.ru/notify/'

bot = Bot(token=TOKEN_NOTIFY)
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
        webhook_path='/notify/',
        on_startup=set_webhook,
        skip_updates=True,
        host='0.0.0.0',
        port=5000,
    )
