from fastapi import FastAPI, Depends
from api.routers import categories, products

app = FastAPI()
app.include_router(products.router)


@app.get("/")
async def root():
    return {"message": "Hello"}
