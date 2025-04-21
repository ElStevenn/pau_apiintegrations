import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from config import DB_HOST, DB_PASSWORD, DB_USERNAME, DB_NAME
from .models import Base

print(DB_HOST, DB_PASSWORD, DB_USERNAME, DB_NAME)
async_engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)
SQLALCHEMY_DATABASE_URI = f'postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}'


async def get_tables():
    async with async_engine.connect() as conn:  
        tables = list(Base.metadata.tables.keys())  
        print("these are the tables -> ", tables)
        return tables

if __name__ == "__main__":
    asyncio.run(get_tables())