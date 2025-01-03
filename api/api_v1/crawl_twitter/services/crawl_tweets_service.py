import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from typing import Dict, List, cast, Optional
from sqlmodel import Session, case, select
from twikit_main.twikit import Client
from celery import Task
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert

from models.crawl_accounts import Account
from models.cookies import Cookie
from models.api_usage import ApiUsage
from schemas.add_tweet_request import AddTweetRequest
from ...tweets.services.add_tweet_service import add_tweet



def get_available_accounts(
    db: Session, api_name: str, rate_limit: int
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
                ApiUsage.is_banned.is_(False),
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


# def reset_api_usage_if_needed(db: Session, account_id, api_name: str):
#     query = (
#         insert(ApiUsage)
#         .values(
#             account_id=account_id,
#             api_name=api_name,
#             request_count=0,
#         )
#         .on_conflict_do_update(
#             index_elements=["account_id", "api_name"],
#             index_where=ApiUsage.last_reset < datetime.now() - timedelta(minutes=15),
#             set_={"request_count": 0, "last_reset": datetime.now()},
#         )
#     )
#     db.exec(query)
#     db.commit()

def reset_api_usage_if_needed(db: Session):
    query = (
        update(ApiUsage)
        .where(
            ApiUsage.last_reset < datetime.now() - timedelta(minutes=15),
        )
        .values(last_reset=datetime.now(), request_count=0)
    )
    db.exec(query)

def mark_account_banned(db: Session, account_id: int):
    """Mark an account as banned"""
    query = update(Account).where(Account.id == account_id).values(is_banned=True)
    db.exec(query)
    db.commit()


def mark_api_banned(db: Session, account_id: int, api_name: str):
    """Mark an api as banned"""
    query = update(ApiUsage).where(
        and_(ApiUsage.account_id == account_id, ApiUsage.api_name == api_name)
    ).values(is_banned=True)
    db.exec(query)
    db.commit()


import pprint as pp
def crawl_tweets(db: Session, screen_name: str, limit: int):
    reset_api_usage_if_needed(db)
    tasks = []
    accounts = get_available_accounts(db, "get_user_by_screen_name", limit)

    task = call_crawl_tweet_tasks(screen_name, accounts[0])
    if task:
        tasks.append(task)
    return tasks


def call_crawl_tweet_tasks(screen_name: str, account: Dict):
    from crawl_tweet_tasks import entry_task

    try:
        task = cast(Task, entry_task).apply_async(
            kwargs=dict(screen_name=screen_name, account=account)
        )
        return task
    except Exception:
        print(traceback.format_exc())
        return None

