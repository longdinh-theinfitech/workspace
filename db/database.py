from sqlalchemy import create_engine
from sqlmodel import Session
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@base-db:5432/lookback'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_master_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
