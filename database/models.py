from sqlalchemy import BigInteger, String, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
import datetime

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase): pass

class User(Base):
    __tablename__ = 'users'
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100), nullable=True)

class Request(Base):
    __tablename__ = 'requests'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20)) # donor/beneficiary
    branch: Mapped[str] = mapped_column(String(50))
    governorate: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)