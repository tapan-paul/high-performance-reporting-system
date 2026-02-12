"""
Data Orchestrator
-----------------
Coordinates ingestion, validation, and persistence of data
from multiple source types.
"""

import logging
import asyncio
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from app.ingestors.kakfa_ingestor import KafkaIngestor
from app.ingestors.base_ingestor import BaseIngestor
from app.ingestors.csv_ingestor import CSVIngestor
from app.ingestors.json_ingestor import JSONIngestor
from app.schemas.data_schema import DataRecord
from app.core.config import settings
from app.crud.storage import save_ingestion_batch, save_error_batch

logger = logging.getLogger(__name__)


class DataOrchestrator:
    """
    Coordinates the end-to-end data ingestion pipeline:
    Ingestor → Validation → Storage.
    """

    def __init__(self, ingestors: Dict[str, BaseIngestor] | None = None):
        self._ingestors = ingestors or {
            "csv": CSVIngestor(),
            "json": JSONIngestor(),
            "kafka": KafkaIngestor()
        }

    async def process(
        self,
        db: AsyncSession,
        raw_data: dict,
        source_type: str,
        source_ref: str | None = None,
    ) -> None:
        """
        Process a single record (Kafka-style ingestion).
        Kafka controls the stream; orchestrator handles validation + persistence.
        """
        try:
            validated = DataRecord(**raw_data)

            await save_ingestion_batch(
                db,
                [{
                    "type": source_type,
                    "source_ref": source_ref,
                    "raw": raw_data,
                    "validated": validated,
                }]
            )

            logger.info(
                "Processed Kafka message %s from %s",
                validated.external_id,
                source_ref,
            )

        except ValidationError as ve:
            await save_error_batch(
                db,
                [{
                    "source_type": source_type,
                    "source_path": source_ref,
                    "raw_content": str(raw_data),
                    "error_message": str(ve),
                }]
            )



    async def execute(self, db: AsyncSession, source_type: str, source_path: str):

        ingestor = self._ingestors.get(source_type.lower())
        staging_batch = []
        error_batch = []

        async for raw_data in ingestor.stream_data(source_path):
            try:
                validated = DataRecord(**raw_data)
                staging_batch.append({
                    "type": source_type,
                    "raw": raw_data,
                    "validated": validated
                })

                if len(staging_batch) >= settings.BATCH_SIZE:
                    await save_ingestion_batch(db, staging_batch)
                    staging_batch.clear()
                    ## finished a heavy batch;  pause for a microsecond to let the Event Loop continue on other work
                    await asyncio.sleep(0)

            except ValidationError as ve:
                error_batch.append({
                    "source_type": source_type,
                    "source_path": source_path,
                    "raw_content": str(raw_data),
                    "error_message": str(ve)
                })

                if len(error_batch) >= settings.BATCH_SIZE:
                    await save_error_batch(db, error_batch)
                    error_batch.clear()

     
        if staging_batch:
            await save_ingestion_batch(db, staging_batch)
            logger.info("Flushed final staging batch: %d records", len(staging_batch))

        if error_batch:
            await save_error_batch(db, error_batch)
            logger.info("Flushed final error batch: %d records", len(error_batch))