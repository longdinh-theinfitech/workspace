from typing import Optional
from sqlmodel import Field, Column, String
from .base_model import BaseModel
from sqlalchemy import UniqueConstraint, Integer, ForeignKey

class Lookback(BaseModel, table=True):
    __tablename__: str = "lookbacks"
    __table_args__ = (UniqueConstraint("screen_name", name="user_unique"),)

    screen_name: str = Field(sa_column=Column(String(255), ForeignKey("users.screen_name"), nullable=False, comment="Twitter ID"))
    lookback_msg: str = Field(sa_column=Column(String(2000), nullable=False, comment="Lookback Message"))

