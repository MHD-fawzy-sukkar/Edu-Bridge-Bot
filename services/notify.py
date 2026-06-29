import logging
from aiogram import Bot
from config import GROUP_ID, ERRORS_TOPIC

async def notify_admin(bot: Bot, error_message: str):
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=ERRORS_TOPIC,
            text=f"⚠️ خطأ في البوت:\n{error_message}"
        )
    except Exception as e:
        logging.error(f"Failed to send error notification: {e}")