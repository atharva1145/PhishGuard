"""
PhishGuard Backend Main Application
FastAPI initialization, CORS configuration, SQLite database bootstrap, and route registration.
"""

from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import ALLOWED_ORIGINS, PROJECT_NAME, VERSION, API_V1_STR
from backend.app.database.db import init_db
from backend.app.api.routes import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("phishguard_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown hooks."""
    logger.info("Initializing PhishGuard services and local database...")
    init_db()
    logger.info("PhishGuard Backend startup complete.")
    yield
    logger.info("PhishGuard Backend shutting down.")


app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description="Explainable AI Phishing Detection Platform REST API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration restricted strictly to development frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global safe exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred during request processing. Please try again later."
        }
    )


# Mount API routes
app.include_router(api_router, prefix=API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": PROJECT_NAME,
        "version": VERSION,
        "status": "online",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
