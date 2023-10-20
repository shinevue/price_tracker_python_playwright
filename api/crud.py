from sqlalchemy import select
from sqlalchemy.orm import Session, DeclarativeMeta
from typing import Type, Union

from database import models as m
from database.models import MECategories, MEProducts, MEPrices


class CRUDBase:
    def __init__(self, model: Type[MECategories] | Type[MEProducts] | Type[MEPrices]):
        self.model = model

    def create(self):
        pass

    def get(self, session: Session, item_id: int):
        q = select(self.model).where(self.model.id == item_id)
        return session.execute(q).first()

    def get_multi(self):
        pass

    def delete(self):
        pass


