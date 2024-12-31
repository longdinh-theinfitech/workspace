from typing import Optional, List
from pydantic import Field

from .base_response_model import BaseModel

class CrawlPersonRequest(BaseModel):
    screen_name: str = Field(None, title="スクリーンネーム")


class CrawlTweetsRequest(BaseModel):
    twitter_id: str = Field(None, title="ユーザーID")
    tweet_type: str = Field(None, title="ツイートタイプ")
