"""Model package initializer.

Importing this module registers all SQLAlchemy models so that relationships
resolve correctly regardless of import order.
"""

from api.models.articles import Article
from api.models.users import User

__all__ = ("Article", "User")
