from sqlalchemy import (
    Column, String, Float, DateTime, Text, ForeignKey, Boolean,
    Integer, Numeric, func, Date, Enum, CheckConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declared_attr
import uuid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

Base = declarative_base()

class PasswordEncryption:
    def __init__(self, time_cost=2, memory_cost=102400, parallelism=8, hash_len=16, salt_len=16):
        self.hasher = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len
        )
    
    def encrypt_password(self, password: str) -> str:
        return self.hasher.hash(password)
    
    def verify_password(self, hashed: str, password: str) -> bool:
        try:
            return self.hasher.verify(hashed, password)
        except VerifyMismatchError:
            return False

password_hasher = PasswordEncryption()

# =========================================================
# BASE USER MODEL
# =========================================================
class BaseUser(Base):
    __tablename__ = "base_user"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    # Relationships
    credentials = relationship(
        "BaseCredentials",
        back_populates="user",
        uselist=False,
        lazy="selectin"
    )
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")

"""
class Profile(Base):
    __tablename__ = "profile"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(pgUUID(as_uuid=True), ForeignKey("base_user.id", ondelete="CASCADE"), nullable=False)
"""

# =========================================================
# INTEGRATIONS
# =========================================================

class Integration(Base):
    __tablename__ = "integration"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(pgUUID(as_uuid=True), ForeignKey("base_user.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    type = Column(String, nullable=False, default="unidirectional") # MVP only unidirectional
    status = Column(String, default="draft")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("BaseUser", back_populates="integrations")
    api_connections = relationship("APIConnection", back_populates="integration", cascade="all, delete-orphan")

class APIConnection(Base):
    __tablename__ = "api_connection"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(pgUUID(as_uuid=True), ForeignKey("integration.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    base_url = Column(Text, nullable=False)
    api_documentation_url = Column(Text, nullable=False)

    # Relationships
    integration = relationship("Integration", back_populates="api_connections")
    api_credentials = relationship("APICredentials", back_populates="api_connection", cascade="all, delete-orphan")

class APICredentials(Base):
    __tablename__ = "api_credentials"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_connection_id = Column(pgUUID(as_uuid=True), ForeignKey("api_connection.id", ondelete="CASCADE"), nullable=False)

    auth_type = Column(String, nullable=False)
    
    api_key_encrypted = Column(Text, nullable=True)
    api_secret_encrypted = Column(Text, nullable=True)
    bearer_token_encrypted = Column(Text, nullable=True)
    username_encrypted = Column(Text, nullable=True)
    password_encrypted = Column(Text, nullable=True)
    passphrase_encrypted = Column(Text, nullable=True)

    extra_config = Column(JSON, nullable=True)

    # Relationships
    api_connection = relationship("APIConnection", back_populates="api_credentials")

# ==========================================================
# CREDENTIALS
# ==========================================================

class BaseCredentials(Base):
    __tablename__ = "base_credentials"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(pgUUID(as_uuid=True), ForeignKey("base_user.id", ondelete="CASCADE"), nullable=False)
    hashed_password = Column(String, nullable=False)

    user = relationship("BaseUser", back_populates="credentials", uselist=False)

    @property
    def password(self):
        """Write-only property for password assignment."""
        raise AttributeError("password is write-only")

    @password.setter
    def password(self, plain_password: str):
        self.hashed_password = password_hasher.encrypt_password(plain_password)

    def verify_password(self, password: str) -> bool:
        """Verify a provided plaintext password."""
        return password_hasher.verify_password(self.hashed_password, password)

# =========================================================
# MIGRATION FOOTER (OPCIONAL)
# =========================================================
"""
 - ../../venv/bin/python ../../venv/bin/alembic upgrade head
 - ../../venv/bin/python ../../venv/bin/alembic revision --autogenerate -m "Updating"
 ...
"""
