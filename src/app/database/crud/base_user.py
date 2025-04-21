
from quart import abort

from sqlalchemy import select, update, insert, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.inspection import inspect

from functools import wraps

from ..database import async_engine
from ..models import BaseUser, BaseCredentials

def db_connection(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                try:
                    result = await func(session, *args, **kwargs)
                    return result
                except OSError:
                     abort(503, description="DB connection in the server does not work, maybe the container is not running or IP is wrong since you've restarted the node")
                except IntegrityError as e:
                    await session.rollback()
                    abort(400, description=str(e))
                # except DBAPIError:
                #     await session.rollback()
                #     abort(400, description="DB connection error")
    return wrapper



"""CRUD operations for the User Table"""
class UserService:
    @staticmethod
    @db_connection
    async def create(session: AsyncSession, data: dict):
        user = BaseUser(username=data["username"],
                        email=data["email"])

        credentials = BaseCredentials()
        credentials.password = data["password"]
        user.credentials = credentials

        session.add(user)
        await session.flush()   

        return {                 
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
        }


    @staticmethod
    @db_connection
    async def get(session: AsyncSession, user_id: str):
        stmt = select(BaseUser).where(BaseUser.id == user_id)
        result = await session.execute(stmt)

        user = result.scalars().first()
        if not user:
            abort(404, description="User not found")

        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
        }

    @staticmethod
    @db_connection
    async def authenticate(session: AsyncSession, email: str, plain_password: str):
        stmt = (select(BaseUser)
                .options(joinedload(BaseUser.credentials))
                .where(BaseUser.email == email))

        user = (await session.execute(stmt)).scalars().first()

        if not user or not user.credentials:
            abort(401, description="Invalid email or password")

        if not user.credentials.verify_password(plain_password):
            abort(401, description="Invalid email or password")

        return {
            "id":       str(user.id),
            "email":    user.email,
            "username": user.username,
        }

    @staticmethod
    @db_connection
    async def update(session: AsyncSession, user_id: str, data: dict):
        stmt = (
            update(BaseUser)
            .where(BaseUser.id == user_id)
            .values(**data)
            .returning(BaseUser)
        )
        result = await session.execute(stmt)
        user = result.scalars().first()
        if not user:
            abort(404, description="User not found")

        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
        }

    @staticmethod
    @db_connection
    async def delete(session: AsyncSession, user_id: str):
        user = await session.get(BaseUser, user_id)

        if not user:
            abort(404, description="User not found")

        await session.delete(user)

        return {"status": "deleted", "user_id": str(user_id)}



async def main_unit_test():
    new_user = await UserService.authenticate("","")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main_unit_test())