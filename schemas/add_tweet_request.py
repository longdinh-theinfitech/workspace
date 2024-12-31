from typing import Optional, List
from pydantic import Field

from .base_response_model import BaseModel


class AddTweetRequest(BaseModel):
    tweet_id: str = Field(None, title="ツイートID")
    user_id: int = Field(None, title="ユーザーID")
    created_at: str = Field(None, title="作成日時")
    text: str = Field(None, title="テキスト")
    is_quote_status: bool = Field(None, title="引用ツイート")
    reply_count: int = Field(None, title="リプライ数")
    favorite_count: int = Field(None, title="お気に入り数")
    view_count: int = Field(None, title="ビュー数")
    retweet_count: int = Field(None, title="リツイート数")
    retweeted_tweet_id: Optional[str] = Field(None, title="リツイートツイートID")
    hashtags: Optional[List[str]] = Field(None, title="ハッシュタグ")
