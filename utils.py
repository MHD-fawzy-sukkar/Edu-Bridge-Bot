import asyncio
import json
import os

from aiohttp.client_exceptions import ClientConnectorError

from config import (GROUP_ID, ERRORS_TOPIC, BANNED_USERS_FILE)


async def notify_admin(bot, error_message: str):
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=ERRORS_TOPIC,
            text=f"⚠️ خطأ في البوت:\n{error_message}",
        )
    except Exception as e:
        print(f"Failed to send error notification: {e}")


async def retry(bot, func, max_attempts=3, delay=0.5):
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return await func()

        except ClientConnectorError as e:
            last_exception = e

            print(f"Retry {attempt + 1} failed: {e}")

            await notify_admin(
                bot,
                f"ClientConnectorError on attempt {attempt + 1}: {e}",
            )

            if attempt < max_attempts - 1:
                await asyncio.sleep(delay * (2 ** attempt))

    raise last_exception


def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        return set()

    with open(BANNED_USERS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_banned_users(banned_users):
    with open(BANNED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(banned_users), f, ensure_ascii=False, indent=2)


banned_users = load_banned_users()