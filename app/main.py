from fastapi import FastAPI
from app.api.routes import router
from database import init_db
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Receptionist AI",
    description="Voice-based AI assistant backend",
    version="0.1.0"
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
init_db()

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Receptionist AI backend is running"}
