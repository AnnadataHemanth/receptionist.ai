from fastapi import FastAPI
from app.api.routes import router
from database import init_db
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI(
    title="Jarvis AI Assistant",
    description="Voice-based AI assistant backend",
    version="0.1.0"
)
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")
init_db()

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Jarvis backend is running"}
