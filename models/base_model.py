from typing import Any

from sqlalchemy import BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import Field, SQLModel

Base = declarative_base()


class BaseModel(SQLModel):
    __abstract__ = True
    id: int = Field(sa_type=BIGINT, default=None, primary_key=True)

    def update_by_dict(self, data: dict[str, Any]):
        for key in data:
            if hasattr(self, key):
                setattr(self, key, data[key])
