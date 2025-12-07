import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router

from app.db.base import Base, engine
from app.db import models
from fastapi.staticfiles import StaticFiles
from app.api.v1.ws import router as ws_router
from app.core.error_handlers import register_exception_handlers

# Ensure data directory exists for SQLite database
os.makedirs("data", exist_ok=True)

# Create tables at startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chili Backend",
    version="0.1.0",
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(ws_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"status": "success", "data": {"message": "Welcome"}}
