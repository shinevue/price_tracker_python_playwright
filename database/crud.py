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

    def read_one(self, db: Session, id):
        query = select(self.model).where(self.model.id == id)
        return db.execute(query).first()

    def read_multi(
        self,
        db: Session,
        skip=0,
        limit=100,
        sort_col: str | None = None,
        sort_order: str = "asc",
        filters: list | None = None,
    ):
        query = select(self.model)
        if filters:
            query = select(self.model).where(*filters).where(self.model)
        if sort_col:
            model_column = getattr(self.model, sort_col, None)
            if model_column is None:
                raise ValueError(f"Invalid column name: {sort_col}")
            query = query.order_by(model_column.asc()) if sort_order == "asc" else query.order_by(model_column.desc())
        query = query.offset(skip).limit(limit)
        return db.execute(select(self.model).offset(skip).limit(limit)).all()

    def update(self, db: Session, id, obj_in):
        db.execute(update(self.model).where(self.model.id == id).values(obj_in))
        db.commit()

    def delete(self, db: Session, id):
        db.execute(delete(self.model).where(self.model.id == id))
        db.commit()
