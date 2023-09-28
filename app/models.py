from sqlalchemy import Column, Integer, String
from .database import Base  # 他のファイルからのインポート


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    status = Column(String(50))
