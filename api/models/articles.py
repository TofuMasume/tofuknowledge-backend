from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.db.db import Base


class Article(Base):
    __tablename__ = "articles"

    article_id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.user_id"))
    path = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    summary = Column(Text)

    author = relationship("User", back_populates="articles")
