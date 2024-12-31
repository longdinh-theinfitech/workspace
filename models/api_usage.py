from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BIGINT,
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    Text,
    UniqueConstraint,
    ForeignKeyConstraint,
)
from sqlmodel import Field

from .base_model import BaseModel


class ApiUsage(BaseModel, table=True):
    __tablename__: str = "api_usage"

    __table_args__ = (
        UniqueConstraint("account_id", "api_name", name="api_usage_account_id_api_name_key"),
        ForeignKeyConstraint(["account_id"], ["accounts.id"], name="api_usage_account_id_fkey"),
    )

    account_id: Optional[int] = Field(sa_type=BIGINT, default=None)

    api_name: Optional[str] = Field(default=None, sa_column=Column(Text))

    request_count: Optional[int] = Field(
        sa_column=Column(Integer, nullable=True), default=None
    )

    is_banned: Optional[bool] = Field(
        default=None, sa_column=Column(Boolean, nullable=True)
    )

    last_reset: datetime = Field(
        default=None, sa_column=Column(TIMESTAMP, server_default=None)
    )
