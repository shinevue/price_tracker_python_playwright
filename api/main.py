from fastapi import FastAPI, Depends
from routers import categories, products

app = FastAPI()
app.include_router(products.router)


@app.get("/")
async def root():
    return {"message": "Hello"}
