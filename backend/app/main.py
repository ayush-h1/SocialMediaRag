from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ===== App factory =====
def create_app() -> FastAPI:
    """
    ASGI app-factory used by uvicorn with `--factory`.

    Keeps startup FAST so Render can detect the open port immediately.
    Any heavy RAG/model initialization should be lazy (see vectorstore.get_vectorstore()).
    """
    app = FastAPI(
        title="SocialMediaRAG",
        version=os.getenv("APP_VERSION", "0.1.0"),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # --- CORS ---
    # Comma-separated origins in env; defaults to "*"
    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
    allow_origins: List[str] = (
        [o.strip() for o in raw_origins.split(",")] if raw_origins else ["*"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Include API routers under /api ---
    api_prefix = os.getenv("API_PREFIX", "/api")

    # Import routers defensively so a missing optional module doesn't crash startup
    def _maybe_include(module_path: str, router_name: str = "router") -> None:
        try:
            module = __import__(module_path, fromlist=[router_name])
            router = getattr(module, router_name)
            app.include_router(router, prefix=api_prefix)
        except Exception as e:  # noqa: BLE001
            # Log to stdout; the app should still boot
            print(f"[main] Skipping router '{module_path}': {e}")

    # Core/basic routes (add or remove as your project has them)
    _maybe_include("app.routes.health")   # /api/health
    _maybe_include("app.routes.auth")     # /api/auth/*
    _maybe_include("app.routes.social")   # /api/social/* (optional)
    _maybe_include("app.routes.search")   # /api/search
    _maybe_include("app.routes.ingest")   # /api/ingest/*
    _maybe_include("app.routes.trends")   # /api/trends/*

    # --- Static UI ---
    # We copy Vite's dist → backend/app/static at build time.
    base_dir = Path(__file__).resolve().parent
    static_dir = base_dir / "static"

    if static_dir.exists():
        # html=True serves index.html for unknown paths (SPA fallback)
        app.mount(
            "/", StaticFiles(directory=str(static_dir), html=True), name="static"
        )
    else:
        print(f"[main] Static directory not found: {static_dir} (API only mode)")

    # --- Optional non-blocking warmup of RAG in a background thread ---
    if os.getenv("RAG_EAGER_INIT", "false").lower() in {"1", "true", "yes", "on"}:
        def _warmup() -> None:
            try:
                print("[main] RAG eager warm-up started")
                from app.services.vectorstore import get_vectorstore  # lazy import
                _ = get_vectorstore()
                print("[main] RAG eager warm-up complete")
            except Exception as exc:  # noqa: BLE001
                print(f"[main] RAG eager warm-up failed: {exc}")

        threading.Thread(target=_warmup, daemon=True).start()

    return app


# Backwards compatible export for non-factory usage (NOT used by Render command)
# If someone runs `uvicorn app.main:app`, they'll still get a FastAPI instance.
app = create_app()


