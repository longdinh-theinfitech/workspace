from sqlmodel import Session, select, update
from models.users import User
from schemas.users_schema import UserCreateRequest


def create_user(db: Session, request: UserCreateRequest):
    existing_user = db.exec(select(User).where(User.twitter_id == request.twitter_id)).first()
    if existing_user:
        db.exec(update(User).where(User.twitter_id == request.twitter_id).values(**request.model_dump()))
        db.commit()
        db.refresh(existing_user)
        return existing_user.model_dump()

    new_user = User(
        twitter_id=request.twitter_id,
        name=request.name,
        screen_name=request.screen_name,
        description=request.description,
        is_blue_verified=request.is_blue_verified,
        verified=request.verified,
        followers_count=request.followers_count,
        following_count=request.following_count,
        media_count=request.media_count,
        statuses_count=request.statuses_count
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user.model_dump()
