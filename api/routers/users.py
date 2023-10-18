from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, ForeignKey, DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declarative_base