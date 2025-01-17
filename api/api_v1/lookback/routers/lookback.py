from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from db.database import get_master_db
from schemas.lookback_request import LookbackRequest
from schemas.lookback_response import LookbackResponse
from ...crawl_twitter import services as crawl_service
from ...users.services.get_users_details import get_user_detail_by_screen_name
from models.lookbacks import Lookback
import time
import json

router = APIRouter()

@router.post("/generate_lookback", response_model=LookbackResponse)
async def generate_lookback(request: LookbackRequest, db: Session = Depends(get_master_db)):
    limit_accounts = 5
    query = db.exec(select(Lookback).where(Lookback.screen_name.ilike(f"{request.screen_name}"))).first()

    if query:
        twitter_account = get_user_detail_by_screen_name(db, request.screen_name)
        return LookbackResponse(
            name=twitter_account.name,
            screen_name=twitter_account.screen_name,
            followers_count=twitter_account.followers_count,
            following_count=twitter_account.following_count,
            is_blue_verified=twitter_account.is_blue_verified,
            **json.loads(query.model_dump()["lookback_msg"])
        )
    
    result = crawl_service.crawl_tweets(db, request.screen_name, limit_accounts)
    response = None
    start_time = time.time()
    while response is None and (time.time() - start_time) < 50:
        response = db.exec(select(Lookback).where(Lookback.screen_name.ilike(f"{request.screen_name}"))).first()
        time.sleep(0.5)
    try:
        twitter_account = get_user_detail_by_screen_name(db, request.screen_name)
        return LookbackResponse(
            name=twitter_account.name,
            screen_name=twitter_account.screen_name,
            followers_count=twitter_account.followers_count,
            following_count=twitter_account.following_count,
            is_blue_verified=twitter_account.is_blue_verified,
            **json.loads(response.model_dump()["lookback_msg"])
        )
    except Exception as e:
        return {}
