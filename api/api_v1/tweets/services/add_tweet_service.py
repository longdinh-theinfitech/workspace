from sqlmodel import Session, select, update
from models.tweets import Tweet
from schemas.add_tweet_request import AddTweetRequest

def add_tweet(db: Session, request: AddTweetRequest):
    existing_tweet = db.exec(select(Tweet).where(Tweet.tweet_id == request.tweet_id)).first()
    if existing_tweet:
        db.exec(update(Tweet).where(Tweet.tweet_id == request.tweet_id).values(**request.model_dump()))
        db.commit()
        db.refresh(existing_tweet)
        return existing_tweet.model_dump()
    
    new_tweet = Tweet(
        tweet_id=request.tweet_id,
        user_id=request.user_id,
        created_at=request.created_at,
        text=request.text,
        is_quote_status=request.is_quote_status,
        reply_count=request.reply_count,
        favorite_count=request.favorite_count,
        view_count=request.view_count,
        retweet_count=request.retweet_count,
        retweeted_tweet_id=request.retweeted_tweet_id,
        hashtags=request.hashtags,
    )
    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)

    return new_tweet.model_dump()
