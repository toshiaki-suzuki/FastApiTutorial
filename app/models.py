from pydantic import BaseModel as PydanticBaseModel, constr, validator
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
    name: constr(min_length=6, max_length=50)
    status: int

    @validator("status", pre=True, always=True)
    def validate_status(cls, value):
        if value not in [0, 1]:
            raise ValueError("Status must be either 0 or 1")
        return value
