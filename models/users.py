from typing import Optional

from sqlalchemy import Column, String, Integer, Boolean, UniqueConstraint
from sqlmodel import Field

from .base_model import BaseModel


class User(BaseModel, table=True):
    __tablename__: str = "users"
    __table_args__ = (
        UniqueConstraint("screen_name", name="screen_name_unique"),
        {"comment": "ユーザー"},
    )

    twitter_id: str = Field(sa_column=Column(String(255), nullable=False, comment="Twitter ID"))
    name: str = Field(sa_column=Column(String(255), nullable=False, comment="名前"))
    screen_name: str = Field(sa_column=Column(String(255), nullable=False, comment="スクリーンネーム"))
    description: Optional[str] = Field(sa_column=Column(String(255), nullable=True, comment="説明"))
    is_blue_verified: Optional[bool] = Field(default=False, sa_column=Column(Boolean, default=False))
    verified: Optional[bool] = Field(default=None, sa_column=Column(Boolean, nullable=True))
    followers_count: Optional[int] = Field(sa_column=Column(Integer, nullable=True), default=0)
    following_count: Optional[int] = Field(sa_column=Column(Integer, nullable=True), default=0)
    media_count: Optional[int] = Field(sa_column=Column(Integer, nullable=True), default=0)
    statuses_count: Optional[int] = Field(sa_column=Column(Integer, nullable=True), default=0)
