from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

async_engine = create_async_engine(get_settings().DATABASE_URL)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    session = async_session()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    else:
        await session.commit()
    finally:
        await session.close()
