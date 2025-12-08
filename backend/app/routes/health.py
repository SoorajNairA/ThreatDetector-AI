"""Health check endpoint"""
from fastapi import APIRouter
from app.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    """
    Health check endpoint to verify service is running.
    
    Returns:
        HealthResponse with status "ok"
    """
    return {"status": "ok"}
