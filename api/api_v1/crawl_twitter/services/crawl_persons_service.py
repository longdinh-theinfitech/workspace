import os
import load_dotenv

from twikit_main.twikit import Client
from sqlmodel import Session
from schemas.users_schema import UserCreateRequest
from ...users.services.user_create_request import create_user

load_dotenv.load_dotenv()


async def crawl_person(db: Session, screen_name: str):
    client = Client(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        + "AppleWebKit/537.36 (KHTML, like Gecko) "
        + "Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        language="ja",
    )
    client.set_cookies(
        cookies=dict(ct0=os.getenv('ct0'),
                    auth_token=os.getenv('auth_token'))
    )
    user = await client.get_user_by_screen_name(screen_name)

    person = UserCreateRequest(
        twitter_id=user.id,
        name=user.name,
        screen_name=user.screen_name,
        description=user.description,
        is_blue_verified=user.is_blue_verified,
        verified=user.verified,
        followers_count=user.followers_count,
        following_count=user.following_count,
        media_count=user.media_count,
        statuses_count=user.statuses_count
    )
    return create_user(db, person) 
