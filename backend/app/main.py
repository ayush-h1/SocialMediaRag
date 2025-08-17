# backend/app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Routers
from .routes import health, social, auth, ingest, search, trends

# Load .env for local dev (Render injects env vars automatically)
load_dotenv()

app = FastAPI(title="SocialMediaRAG")

# ---------- CORS ----------
# Configure allowed origins via env (comma-separated). Defaults cover local dev.
origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
)
origins = [o.strip() for o in origins_env.split(",") if o.strip()]

# Note: credentials cannot be combined with wildcard "*"
allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
if "*" in origins and allow_credentials:
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- API Routers ----------
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(social.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(trends.router, prefix="/api")

# ---------- Static frontend (served after API so /api/* wins) ----------
# Expecting the Vite build to be copied to backend/app/static/ during build
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
