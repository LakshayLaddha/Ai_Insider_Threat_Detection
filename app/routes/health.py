from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API and database are functioning.
    """
    try:
        # Use text() function to wrap the raw SQL
        db.execute(text("SELECT 1")).fetchone()
        return {"status": "ok", "message": "Service is healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )