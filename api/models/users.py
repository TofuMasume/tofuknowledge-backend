from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from api.db.db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(String(32), nullable=False)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    articles = relationship("Article", back_populates="author")
