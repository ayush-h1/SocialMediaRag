# backend/app/main.py
import os
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

log = logging.getLogger("uvicorn.error")


def create_app() -> FastAPI:
    app = FastAPI(title="SocialMediaRAG")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*", "http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Light routers only (must be fast to import)
    from .routes import health, auth
    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api/auth")

    # Serve built frontend
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    @app.on_event("startup")
    async def _lazy_mount_heavy():
        """
        Defer heavy imports (chromadb, sentence-transformers, etc.)
        so Uvicorn can bind to $PORT immediately.
        """
        def _load():
            try:
                # Import here so model/vector DB loads are deferred
                from .routes import social, search, ingest, trends
                app.include_router(social.router, prefix="/api")
                app.include_router(search.router, prefix="/api")
                app.include_router(ingest.router, prefix="/api")
                app.include_router(trends.router, prefix="/api")
                log.info("Heavy routers mounted.")
            except Exception:
                log.exception("Failed to mount heavy routers")

        # Kick off in background; don’t block startup
        asyncio.get_event_loop().call_soon(_load)

    return app


# Uvicorn --factory expects a callable that returns the app
app = create_app()

