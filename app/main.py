from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.api.routes import router
from app.core.config import SECRET_KEY

app = FastAPI(
    title="AI Receptionist API",
    description="An AI-powered receptionist that can handle bookings via SMS and phone calls.",
    version="1.0.0"
)

# Add session middleware (for login system)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)

# Include routes
app.include_router(router)


@app.get("/")
def home():
    return {"message": "AI Receptionist is running 🚀"}