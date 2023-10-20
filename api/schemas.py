from pydantic import BaseModel


class CategoryBase(BaseModel):
    id: int


class ProductBase(BaseModel):
    id: int


class PriceBase(BaseModel):
    id: int
