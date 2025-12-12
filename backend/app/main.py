from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logging_config import configure_logging, get_logger
from app.routes import health, analyze, stats, keys, ml, logs

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Guardian Security Platform",
    description="Backend API for real-time threat detection and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

allowed_origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:3000",  # Always allow localhost for development
    "http://localhost:8000",
]

if settings.APP_ENV == "dev":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if settings.APP_ENV != "dev" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(stats.router)
app.include_router(keys.router)
app.include_router(ml.router)
app.include_router(logs.router)


@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Guardian Security Platform - Starting Up")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"API Key Auth: {'Enabled' if settings.API_KEY else 'Disabled'}")
    logger.info(f"Supabase URL: {settings.SUPABASE_URL}")
    logger.info(f"Frontend Origin: {settings.FRONTEND_ORIGIN}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Guardian Security Platform - Shutting Down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.APP_ENV == "dev"
    )
