from datetime import datetime
from typing import Optional, List

from sqlmodel import Field
from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    Boolean,
    Column,
    String,
    Text,
    Integer,
)

from .base_model import BaseModel


class Tweet(BaseModel, table=True):
    __tablename__: str = "tweets"
    __table_args__ = {
        "comment": "ツイート",
    }

    tweet_id: Optional[str] = Field(sa_column=Column(Text, nullable=False, comment="ツイートID"))
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    created_at: Optional[datetime] = Field(sa_column=Column(TIMESTAMP, nullable=False, comment="作成日時"))
    text: Optional[str] = Field(sa_column=Column(Text, nullable=False, comment="テキスト"))
    is_quote_status: Optional[bool] = Field(sa_column=Column(Boolean, nullable=False, default=False, comment="引用ツイート"))
    reply_count: Optional[int] = Field(sa_column=Column(Integer, nullable=False, comment="リプライ数"), default=0)
    favorite_count: Optional[int] = Field(sa_column=Column(Integer, nullable=False, comment="お気に入り数"), default=0)
    view_count: Optional[int] = Field(sa_column=Column(Integer, nullable=False, comment="ビュー数"), default=0)
    retweet_count: Optional[int] = Field(sa_column=Column(Integer, nullable=False, comment="リツイート数"), default=0)
    retweeted_tweet_id: Optional[str] = Field(sa_column=Column(Text, nullable=True, comment="リツイートツイートID"))
    hashtags: Optional[List[str]] = Field(sa_column=Column(ARRAY(String(2048)), nullable=True), default=None)
