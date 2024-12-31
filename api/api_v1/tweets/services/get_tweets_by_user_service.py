from sqlmodel import Session, select
from models.tweets import Tweet


def get_tweets_by_user(db: Session, user_id: int):
    query = select(Tweet).where(Tweet.user_id == user_id)
    query = query.order_by(Tweet.created_at.desc())
    result = db.exec(query).all()
    return result
