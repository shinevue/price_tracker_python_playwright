from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database import models as m
from api.crud import CRUDBase

# TODO import errors
router = APIRouter(prefix='products',
                   tags=['products'])

crud = CRUDBase(m.MEProducts)


@router.get('/{product_id}')
async def read_product(product_id: int,
                       session: Session = Depends(get_db)):
    return crud.get(session=session, item_id=product_id)
