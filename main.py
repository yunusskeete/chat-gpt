"""FastAPI application entry point for PT Lead Qualification Chatbot"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from app.api.webhooks.whatsapp import router as whatsapp_router
from app.database import init_db

# from app.middleware import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Chat-GPT: Chat Gateway for Personal Trainers...")
    init_db()
    logger.info("Database initialized")
    yield
    # # Shutdown (if needed in the future)
    # logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Chat-GPT: Chat Gateway for Personal Trainers",
    description="WhatsApp chatbot gateway for personal trainers to auto-quality leads",
    version="0.0.1",
    lifespan=lifespan,
)

# Add middleware (disabled for now due to form data consumption issue)
# app.add_middleware(RateLimitMiddleware, rate_limit_seconds=3)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PT Lead Qualification Chatbot API",
        "version": "0.0.1",
        "endpoints": {"health": "/health", "whatsapp_webhook": "/webhook/whatsapp"},
    }


# Include routers
app.include_router(whatsapp_router, prefix="/webhook", tags=["webhooks"])


if __name__ == "__main__":
    import uvicorn

    from app.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
