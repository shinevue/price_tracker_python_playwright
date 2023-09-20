from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# declarative base class
class Base(DeclarativeBase):
    pass


class MECategories(Base):
    __tablename__ = "me_categories"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)
    category_path: Mapped[str] = mapped_column(nullable=False)
    time_discovered: Mapped[datetime]
    last_crawl: Mapped[datetime]
    product_count: Mapped[int]

    # Relationships
    products: Mapped[List["MEProducts"]] = relationship()


class MEProducts(Base):
    __tablename__ = 'me_products'

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    product_name: Mapped[str] = mapped_column()
    monitoring: Mapped[int] = mapped_column()
    monitoring_freq: Mapped[int] = mapped_column()
    category_id: Mapped[int] = mapped_column(ForeignKey('me_categories.id'))

    # Relationships
    category: Mapped["MECategories"] = relationship(back_populates='products')
    prices: Mapped[List["MEPrices"]] = relationship()


class MEPrices(Base):
    __tablename__ = 'me_prices'

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('me_products.id'))
    price: Mapped[int]
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now())
    url: Mapped[str]

    # Relationships
    products: Mapped["MEProducts"] = relationship(back_populates='prices')
