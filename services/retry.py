import asyncio
from aiohttp.client_exceptions import ClientConnectorError

async def retry(func, max_attempts=3, delay=0.5):
    last_exception = None
    for attempt in range(max_attempts):
        try:
            return await func()
        except ClientConnectorError as e:
            last_exception = e
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay * (2 ** attempt))
    raise last_exception