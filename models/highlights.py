from typing import Optional
from sqlmodel import Field
from .base_model import BaseModel

class Highlight(BaseModel, table=True):
    __tablename__: str = "highlights"
    __table_args__ = {
        "comment": "ハイライト",
    }

    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    tweet_id: Optional[int] = Field(default=None, foreign_key="tweets.tweet_id", index=True)

