from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.core.orchestrator import DataOrchestrator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ingest")
async def ingest_file(
    file_path: str,
    # Use Query to restrict input to only supported types
    source_type: str = Query("csv", enum=["csv", "json"]),
    db: AsyncSession = Depends(get_db),
):
    orchestrator = DataOrchestrator()

    try:
        summary = await orchestrator.execute(
            db=db,
            source_type=source_type,
            source_path=file_path,
        )
        
        return {
            "status": "success",
            "message": f"Processed {file_path} as {source_type}",
            "summary": summary  # High-value info for the user
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.exception("Unexpected error during ingestion")
        raise HTTPException(status_code=500, detail="Internal server error during ingestion")