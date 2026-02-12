from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.reporting.exporter import ReportExporter
from sqlalchemy import func, select
from app.models.models import ProcessedData, IngestionError

router = APIRouter()

@router.get("/errors/{format}")
async def get_error_report(format: str, db: AsyncSession = Depends(get_db)):
    """
    Download a report of all rows that failed validation.
    """
    content, mime_type = await ReportExporter.export_errors(db, format)

    if content is None:
        return {"message": "No errors found! Great job."}
    return Response(
        content=content, 
        media_type=mime_type,
        headers={"Content-Disposition": f"attachment; filename=error_report.{format}"}
    )

@router.get("/summary")
async def get_ingestion_summary(db: AsyncSession = Depends(get_db)):
    """Quick stats on system health"""

    # Run both counts concurrently
    # pylint: disable=not-callable
    success_stmt = select(func.count(ProcessedData.id))
    error_stmt = select(func.count(IngestionError.id))
    
    success_count = (await db.execute(success_stmt)).scalar() or 0
    error_count = (await db.execute(error_stmt)).scalar() or 0

    total = success_count + error_count
    success_rate = (success_count / total * 100) if total > 0 else 0
    
    return {
        "total_processed": total,
        "successful_records": success_count,
        "validation_failures": error_count,
        "success_rate": f"{success_rate:.2f}%"
    }


@router.get("/report/{format}")
async def download_report(format: str, db: AsyncSession = Depends(get_db)):
    try:
        content, media_type = await ReportExporter.export(db, format.lower())
        
        if content is None:
            return {"message": "Database is empty. Ingest some data first!"}

        # Return the file as a downloadable attachment
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename=report.{format}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))