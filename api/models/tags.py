from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from api.db.db import Base


class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, nullable=False, unique=True)
    tag_name = Column(String(64), nullable=False, unique=True)

    articles = relationship(
        "Article", secondary="article_tags", back_populates="tags"
    )
