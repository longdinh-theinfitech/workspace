from typing import Optional, List
from pydantic import Field

from .base_response_model import BaseModel

class LookbackResponse(BaseModel):
    name : Optional[str] = Field(None, title="名前")
    screen_name: Optional[str] = Field(None, title="ユーザー名")
    followers_count: Optional[int] = Field(None, title="フォロワー数")
    following_count: Optional[int] = Field(None, title="フォロー数")
    posts_count: Optional[int] = Field(None, title="投稿数")
    favorite_count: Optional[int] = Field(None, title="いいね数")
    reply_count: Optional[int] = Field(None, title="リプライ数")
    retweet_count: Optional[int] = Field(None, title="リツイート数")
    view_count: Optional[int] = Field(None, title="ビュー数")
    interest: Optional[List[str]] = Field(None, title="キーワード")
    topics: Optional[List[str]] = Field(None, title="トピック")
    description: Optional[str] = Field(None, title="説明")
                                                                                                                                        