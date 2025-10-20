from sqlalchemy import Column, ForeignKey, Integer

from api.db.db import Base


class ArticleTag(Base):
    __tablename__ = "article_tags"

    article_id = Column(
        Integer, ForeignKey("articles.article_id"), primary_key=True
    )
    tag_id = Column(Integer, ForeignKey("tags.tag_id"), primary_key=True)
