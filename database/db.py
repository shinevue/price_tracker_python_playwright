import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, orm, select
from sqlalchemy.ext.declarative import declarative_base

from database import models

load_dotenv()
SQL_DB_URL = os.environ.get("SQL_DB_URL")

engine = create_engine(SQL_DB_URL)
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_db():
    session = SessionLocal()
    # test_entry = models.MECategories(category_path='/some/path',
    #                                  time_discovered=datetime.now(),
    #                                  product_count=12)
    # session.add(test_entry)
    delete_statement = select(models.MECategories).where(models.MECategories.id==1)
    object_to_delete = session.scalars(delete_statement).first()
    print(object_to_delete)
    session.delete(object_to_delete)
    session.commit()
