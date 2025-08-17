from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import health, social, auth
import os

app = FastAPI(title="SocialMediaRAG")

# CORS (dev-friendly)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(social.router, prefix="/api")

# Serve static (for built frontend, if copied to backend/app/static)
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
