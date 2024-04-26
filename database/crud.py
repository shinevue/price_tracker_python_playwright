from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete


class CRUD:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in):
        db.execute(insert(self.model).values(obj_in))
        db.commit()

    def bulk_create(self, db: Session, obj_in: list):
        db.execute(insert(self.model), obj_in)
        db.commit()

    def read(self, db: Session, id):
        return db.execute(select(self.model).where(self.model.id == id)).first()

    def update(self, db: Session, id, obj_in):
        db.execute(update(self.model).where(self.model.id == id).values(obj_in))
        db.commit()

    def delete(self, db: Session, id):
        db.execute(delete(self.model).where(self.model.id == id))
        db.commit()
