from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import config
from sqlalchemy import delete
from app.models import Postings


engine = create_async_engine(config.DB_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def delete_post(posting_id: int):
    async with async_session() as session:
        stmt = delete(Postings).where(Postings.posting_id == posting_id)
        await session.execute(stmt)
        await session.commit()
