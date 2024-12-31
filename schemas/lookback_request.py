from pydantic import Field

from .base_response_model import BaseModel

class LookbackRequest(BaseModel):
    screen_name: str = Field(None, title="Twitter Screen Name", description="The screen name of the Twitter account to generate a lookback for")
