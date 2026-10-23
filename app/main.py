
from fastapi import FastAPI
from app.database import create_tables
from app.routes import router

create_tables()

app = FastAPI(
    title="API Conversations",
    version="1.0.0"
)

app.include_router(router)
