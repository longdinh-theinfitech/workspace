from typing import Optional
from pydantic import Field

from .base_response_model import BaseModel


class GetTweetByUserRequest(BaseModel):
    user_id: Optional[int] = Field(None, title="ユーザーID")
