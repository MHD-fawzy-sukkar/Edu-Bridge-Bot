from database.models import async_session, User, Request
from sqlalchemy import select

async def add_user(tg_id, telegram_name, username):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, telegram_name=telegram_name, username=f"@{username}"))
        else:
            user.telegram_name = telegram_name
            user.username = f"@{username}"
    
        await session.commit()


async def add_request_data(tg_id, data, username, content):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.username = username
        
        session.add(Request(
            tg_id=tg_id, 
            name=data['name'], 
            type=data['type'],
            branch=data['branch'], 
            governorate=data['governorate'],
            address=data['address'], 
            content=content
        ))
        await session.commit()