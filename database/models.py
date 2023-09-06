from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


# declarative base class
class Base(DeclarativeBase):
    pass


class MECategories(Base):
    __tablename__ = "me_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_path: Mapped[str] = mapped_column(nullable=False)
    time_discovered: Mapped[datetime]
    last_crawl: Mapped[datetime]
    product_count: Mapped[int]
