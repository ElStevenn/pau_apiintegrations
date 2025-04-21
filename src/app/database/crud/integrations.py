from quart import abort

from sqlalchemy import select, update, insert, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.inspection import inspect

from functools import wraps

from ..database import async_engine
from ..models import BaseUser, BaseCredentials, Integration

from .base_user import db_connection





