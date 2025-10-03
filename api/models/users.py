from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from api.db.db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(32))
    email = Column(String(255))
    created_at = Column(DateTime)

    articles = relationship("Article", back_populates="author")
