from typing import Optional
from pydantic import Field

from .base_response_model import BaseModel


class UserCreateRequest(BaseModel):
    twitter_id: str = Field(None, title="Twitter ID")
    name: str = Field(None, title="名前")
    screen_name: str = Field(None, title="スクリーンネーム")
    description: Optional[str] = Field(None, title="説明")
    is_blue_verified: Optional[bool] = Field(False, title="ブルーバッジ")
    verified: Optional[bool] = Field(None, title="認証済み")
    followers_count: Optional[int] = Field(0, title="フォロワー数")
    following_count: Optional[int] = Field(0, title="フォロー数")
    media_count: Optional[int] = Field(0, title="メディア数")
    statuses_count: Optional[int] = Field(0, title="ステータス数")


class UserDetailRequest(BaseModel):
    twitter_id: str = Field(None, title="Twitter ID")

