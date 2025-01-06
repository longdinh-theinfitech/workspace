from sqlmodel import Session, select
from models.users import User


def all_user(db: Session):
    users = db.exec(select(User)).all()
    return users


def get_user_detail(db: Session, twitter_id: str):
    user = db.exec(select(User).where(User.twitter_id == twitter_id)).first()
    return user


def get_user_detail_by_screen_name(db: Session, screen_name: str):
    user = db.exec(select(User).where(User.screen_name.ilike(f"{screen_name}"))).first()
    return user
