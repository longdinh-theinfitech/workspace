from datetime import datetime
from typing import Optional

from sqlalchemy import BIGINT, TIMESTAMP, Boolean, Column, Text, ForeignKeyConstraint
from sqlmodel import Field

from .base_model import BaseModel


class Cookie(BaseModel, table=True):
    __tablename__: str = "cookies"

    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name="cookies_account_id_fkey"
        ),
    )

    account_id: Optional[int] = Field(sa_type=BIGINT, default=None)

    ct0: Optional[str] = Field(default=None, sa_column=Column(Text))

    auth_token: Optional[str] = Field(default=None, sa_column=Column(Text))

    is_valid: Optional[bool] = Field(
        default=None, sa_column=Column(Boolean, nullable=True)
    )

    expires_at: datetime = Field(
        default=None, sa_column=Column(TIMESTAMP, server_default=None)
    )

    created_at: datetime = Field(
        default=None, sa_column=Column(TIMESTAMP, server_default=None)
    )
