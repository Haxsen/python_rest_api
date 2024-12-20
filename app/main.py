from fastapi import FastAPI
from app.routers import invest
from app.models import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(invest.router)

@app.get("/")
async def root():
    return {"message": "Python API is running"}
