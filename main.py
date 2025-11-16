"""FastAPI application entry point for PT Lead Qualification Chatbot"""
from fastapi import FastAPI
from datetime import datetime, timezone
import logging

from app.api.webhooks.whatsapp import router as whatsapp_router
from app.database import init_db
from app.middleware import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PT Lead Qualification Chatbot",
    description="WhatsApp chatbot for qualifying personal training leads",
    version="0.0.1"
)

# Add middleware (disabled for now due to form data consumption issue)
# app.add_middleware(RateLimitMiddleware, rate_limit_seconds=3)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting PT Lead Qualification Chatbot...")
    init_db()
    logger.info("Database initialized")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PT Lead Qualification Chatbot API",
        "version": "0.0.1",
        "endpoints": {
            "health": "/health",
            "whatsapp_webhook": "/webhook/whatsapp"
        }
    }


# Include routers
app.include_router(whatsapp_router, prefix="/webhook", tags=["webhooks"])


if __name__ == "__main__":
    import uvicorn
    from app.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
