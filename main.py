import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramConflictError

# Import configuration
from config import TOKEN, GROUP_ID

# Import routers from handlers
from handlers import start, request, support, admin, general

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log"
)

# --- Setup Bot Commands ---
async def set_commands(bot: Bot):
    # Commands for regular users
    await bot.set_my_commands([
        types.BotCommand(command="start", description="بدء الاستخدام"),
        types.BotCommand(command="stop", description="إلغاء العملية الحالية"),
        types.BotCommand(command="help", description="عرض التعليمات"),
        types.BotCommand(command="info", description="معلومات حول فكرة البوت وكيفية استخدامه")
    ])
    
    # Commands for admins (scoped to the specific admin group)
    await bot.set_my_commands([
        types.BotCommand(command="start", description="بدء الاستخدام"),
        types.BotCommand(command="stop", description="إلغاء العملية الحالية"),
        types.BotCommand(command="help", description="عرض التعليمات"),
        types.BotCommand(command="info", description="معلومات حول فكرة البوت وكيفية استخدامه"),
        types.BotCommand(command="ban", description="حظر مستخدم من البوت"),
        types.BotCommand(command="unban", description="إلغاء الحظر"),
        types.BotCommand(command="replyto", description="الرد على مستخدم")
    ], scope=types.BotCommandScopeChatAdministrators(chat_id=GROUP_ID))

# --- Main Application Entry Point ---
async def main():
    logging.info("✅ Starting bot initialization...")
    print("✅ Starting bot initialization...")
    # Setup bot session and dispatcher
    session = AiohttpSession()
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML, session=session)
    dp = Dispatcher()

    # Register all routers (The order doesn't matter much, but it's good to be organized)
    dp.include_router(start.router)
    dp.include_router(general.router) 
    dp.include_router(request.router)
    dp.include_router(support.router)
    dp.include_router(admin.router)

    try:
        # Drop any pending updates before starting to avoid spam from when the bot was offline
        await bot.delete_webhook(drop_pending_updates=True)
        await set_commands(bot)
        
        logging.info("✅ Bot is polling and ready to receive messages!")
        await dp.start_polling(bot)
    except TelegramConflictError as e:
        logging.error(f"TelegramConflictError during startup: {e}")
    except Exception as e:
        logging.error(f"General error during startup: {e}")
    finally:
        # Always close the session properly when shutting down
        await bot.session.close()
        logging.info("🛑 Bot session closed.")

if __name__ == "__main__":
    asyncio.run(main())