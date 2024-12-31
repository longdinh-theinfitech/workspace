from datetime import datetime
from typing import Optional

from sqlalchemy import TIMESTAMP, Boolean, Column, Text, UniqueConstraint
from sqlmodel import Field

from .base_model import BaseModel


class Account(BaseModel, table=True):
    __tablename__: str = "accounts"

    __table_args__ = (
        UniqueConstraint(
            "email", name="accounts_email_key"
        ),
    )

    email: Optional[str] = Field(default=None, sa_column=Column(Text))

    password: Optional[str] = Field(default=None, sa_column=Column(Text))

    totp_secret: Optional[str] = Field(default=None, sa_column=Column(Text))

    is_active: Optional[bool] = Field(
        default=None, sa_column=Column(Boolean, nullable=True)
    )

    is_banned: Optional[bool] = Field(
        default=None, sa_column=Column(Boolean, nullable=True)
    )

    is_in_use: Optional[bool] = Field(
        default=False, sa_column=Column(Boolean, default=False)
    )

    created_at: datetime = Field(
        default=None, sa_column=Column(TIMESTAMP, server_default=None)
    )
