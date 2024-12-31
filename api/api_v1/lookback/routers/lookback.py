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
    limit_accounts = 15
    result = crawl_service.crawl_tweets(db, request.screen_name, limit_accounts)
    response = None
    start_time = time.time()
    while response is None and (time.time() - start_time) < 120:
        query = db.exec(select(Lookback).where(Lookback.screen_name == request.screen_name))
        response = query.first()
        time.sleep(1)
    twitter_account = get_user_detail_by_screen_name(db, request.screen_name)
    message = response.model_dump()
    return LookbackResponse(
        name=twitter_account.name,
        screen_name=twitter_account.screen_name,
        followers_count=twitter_account.followers_count,
        following_count=twitter_account.following_count,
        **json.loads(message["lookback_msg"])
    )
