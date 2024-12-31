import os
import load_dotenv
import traceback
from datetime import datetime, timedelta

from typing import Dict, List, cast
from sqlmodel import Session, case, select
from twikit_main.twikit import Client
from celery import Task
from sqlalchemy import and_, func, or_, select, update

from models.users import User
from models.crawl_accounts import Account
from models.cookies import Cookie
from models.api_usage import ApiUsage
from schemas.add_tweet_request import AddTweetRequest
from ...tweets.services.add_tweet_service import add_tweet
from crawl_tweet_tasks import entry_task

load_dotenv.load_dotenv()

# client = Client(
#         user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         + "AppleWebKit/537.36 (KHTML, like Gecko) "
#         + "Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
#         language="ja",
#         )

# client.set_cookies(
#     cookies=dict(ct0=os.environ.get('ct0'),
#                 auth_token=os.environ.get('auth_token'))
# )

# async def crawl_tweets_by_type(db: Session, twitter_id: str, tweet_type: str):
#     tweets_list = []
#     more_tweets = await client.get_user_tweets(user_id=twitter_id, tweet_type= tweet_type, count= 20)

#     while(len(tweets_list) < 200 and more_tweets):
#         tweets_list.extend(more_tweets)
#         more_tweets = await more_tweets.next()

#     user = db.exec(select(User).where(User.twitter_id == twitter_id)).first()
#     response = []
#     for tweet in tweets_list:
#         item = AddTweetRequest(
#                 tweet_id=tweet.id,
#                 user_id=user.id,
#                 created_at=tweet.created_at_datetime.isoformat(),
#                 text=tweet.text,
#                 is_quote_status=tweet.is_quote_status,
#                 reply_count=tweet.reply_count,
#                 favorite_count=tweet.favorite_count,
#                 view_count=int(tweet.view_count) if tweet.view_count else 0,
#                 retweet_count=tweet.retweet_count,
#                 retweeted_tweet_id=tweet.retweeted_tweet.id if tweet.retweeted_tweet else None,
#                 hashtags=tweet.hashtags
#             )
#         response.append(add_tweet(db, item))
#     return response


# async def crawl_highlight(db: Session, twitter_id: str):
#     user = db.exec(select(User).where(User.twitter_id == twitter_id)).first()
#     response = []

#     highlight_list = []
#     highlights = await client.get_user_highlights_tweets(user_id=twitter_id)

#     while(len(highlight_list) < 200 and highlights):
#         highlight_list.extend(highlights)
#         highlights = await highlights.next()

#     for tweet in highlight_list:
#         item = AddTweetRequest(
#                 tweet_id=tweet.id,
#                 user_id=user.id,
#                 created_at=tweet.created_at_datetime.isoformat(),
#                 text=tweet.text,
#                 is_quote_status=tweet.is_quote_status,
#                 reply_count=tweet.reply_count,
#                 favorite_count=tweet.favorite_count,
#                 view_count=int(tweet.view_count) if tweet.view_count else 0,
#                 retweet_count=tweet.retweet_count,
#                 retweeted_tweet_id=tweet.retweeted_tweet.id if tweet.retweeted_tweet else None,
#                 hashtags=tweet.hashtags
#             )
#         response.append(add_tweet(db, item))
#     return response

def get_available_accounts(
    db: Session, api_name: str, rate_limit: int = 10
) -> List[Dict]:
    query = (
        select(
            Account.id,
            Account.email,
            Account.password,
            Account.totp_secret,
            Cookie.ct0,
            Cookie.auth_token,
            func.coalesce(ApiUsage.request_count, 0).label("request_count"),
            ApiUsage.last_reset,
        )
        .join(
            Cookie,
            and_(Account.id == Cookie.account_id, Cookie.is_valid.is_(True)),
            isouter=True,
        )
        .join(
            ApiUsage,
            and_(Account.id == ApiUsage.account_id, ApiUsage.api_name == api_name),
            isouter=True,
        )
        .where(
            and_(
                Account.is_active.is_(True),
                Account.is_banned.is_(False),
                or_(
                    Account.is_in_use.is_(False),
                    Account.is_in_use.is_(None),
                ),
                or_(
                    ApiUsage.request_count.is_(None),
                    ApiUsage.request_count < rate_limit,
                    ApiUsage.last_reset < datetime.now() - timedelta(minutes=15),
                ),
            )
        )
        .order_by(
            ApiUsage.last_reset.asc(), func.coalesce(ApiUsage.request_count, 0).asc()
        )
        .limit(1)
    )

    results = db.exec(query).all()
    accounts = []

    for result in results:
        update_query = (
            update(ApiUsage)
            .where(
                and_(
                    ApiUsage.account_id == result.id,
                    ApiUsage.api_name == api_name,
                )
            )
            .values(
                request_count=case(
                    (
                        ApiUsage.last_reset < datetime.now() - timedelta(minutes=15),
                        0,
                    ),
                    else_=ApiUsage.request_count + 1,
                ),
                last_reset=case(
                    (
                        ApiUsage.last_reset < datetime.now() - timedelta(minutes=15),
                        datetime.now(),
                    ),
                    else_=ApiUsage.last_reset,
                ),
            )
        )

        db.exec(update_query)
        accounts.append(
            {
                "id": result.id,
                "email": result.email,
                "password": result.password,
                "totp_secret": result.totp_secret,
                "ct0": result.ct0,
                "auth_token": result.auth_token,
            }
        )

    db.commit()
    return accounts


def reset_api_usage_if_needed(db: Session):
    query = (
        update(ApiUsage)
        .where(
            ApiUsage.api_name == "get_user_tweets",
            ApiUsage.last_reset < datetime.now() - timedelta(minutes=15),
        )
        .values(last_reset=datetime.now(), request_count=0)
    )
    db.exec(query)
    db.commit()


def crawl_tweets(db: Session, screen_name: str, limit: int = 10):
    reset_api_usage_if_needed(db)
    tasks = []
    accounts = get_available_accounts(db, "get_user_tweets", limit)
    task = call_crawl_tweet_tasks(screen_name, accounts[0])
    if task:
        tasks.append(task)
    return tasks


def call_crawl_tweet_tasks(screen_name: str, account: Dict):
    try:
        task = cast(Task, entry_task).apply_async(
            kwargs=dict(screen_name=screen_name, account=account)
        )
        return task
    except Exception:
        print(traceback.format_exc())
        return None
