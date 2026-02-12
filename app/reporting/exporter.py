"""
    ReportExporter is responsible for generating reports of processed data and validation failures.
    It supports multiple formats (CSV, JSON, XLSX) and ensures efficient data retrieval and formatting.
    This class abstracts the reporting logic away from the API layer, allowing for clean separation of concerns.
"""
import io
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ProcessedData
from app.core.config import settings
from app.models.models import ProcessedData, IngestionError # Import both models
import asyncio

class ReportExporter:
    """
    Requirement #4: Multi-format Reporting System.
    Handles both successful records and validation failures.
    """

    @staticmethod
    async def get_report_data(db: AsyncSession):
        result = await db.execute(select(ProcessedData))
        records = result.scalars().all()
        data = [
            {
                "id": r.id,
                "external_id": r.external_id,
                "amount": r.amount,
                "currency": r.currency,
                "status": r.status,
                "processed_at": r.processed_at
            } for r in records
        ]
        return await asyncio.to_thread(pd.DataFrame, data)

    @staticmethod
    async def get_error_data(db: AsyncSession):
        """Helper to fetch validation failures"""
        result = await db.execute(select(IngestionError))
        records = result.scalars().all()
        data = [
            {
                "id": r.id,
                "source": r.source_path,
                "error": r.error_message,
                "raw_payload": r.raw_content,
                "failed_at": r.created_at
            } for r in records
        ]
        return await asyncio.to_thread(pd.DataFrame,data)

    @classmethod
    async def export(cls, db: AsyncSession, format: str):
        df = await cls.get_report_data(db)
        return await cls._generate_bytes(df, format)

    @classmethod
    async def export_errors(cls, db: AsyncSession, format: str):
        """New: Export logic for the Dead Letter table"""
        df = await cls.get_error_data(db)        
        return await cls._generate_bytes(df, format)

    @staticmethod
    async def _generate_bytes(df: pd.DataFrame, format: str):
        """Unified internal method to handle byte conversion asynchronously"""
        if df.empty:
            return None, "No data available"

        fmt = format.lower()
        content_type = settings.REPORT_FORMATS.get(fmt)
        if not content_type:
             raise ValueError(f"Format {fmt} not supported.")

        #  CSV is usually fast, but for 10k rows, thread it anyway
        if fmt == settings.FILE_CSV:
            content = await asyncio.to_thread(lambda: df.to_csv(index=False).encode())
            return content, content_type
        
        # JSON conversion
        if fmt == settings.FILE_JSON:
            content = await asyncio.to_thread(lambda: df.to_json(orient="records").encode())
            return content, content_type
        
        # Excel is the heaviest - definitely needs a thread
        if fmt == settings.FILE_XLSX:
            def to_excel():
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                return output.getvalue()
                
            content = await asyncio.to_thread(to_excel)
            return content, content_type

        raise ValueError(f"Logic error: {fmt} registered but not implemented.")