from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import UUIDType
import uuid

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), index=True)
    status = Column(Integer)


class TaskCreate(PydanticBaseModel):
    name: str
    status: int
