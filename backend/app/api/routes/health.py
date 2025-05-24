from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify API is running correctly
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

