from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ProcessedData, RawData, IngestionError

async def save_error_batch(db: AsyncSession, error_data: list[dict]):
    """
    Persists a batch of validation failures to the IngestionError table.
    """

    # Map the list of dictionaries to SQLAlchemy objects
    objs = [
        IngestionError(
            source_type=data["source_type"],
            source_path=data["source_path"],
            raw_content=data["raw_content"],
            error_message=data["error_message"]
        ) for data in error_data
    ]
    
    db.add_all(objs)
    await db.commit()
    # Important for your 100k test to prevent memory bloat
    db.expunge_all()


async def save_ingestion_batch(db: AsyncSession, batch_data: list[dict]):
    """
    Handles the 'Double Batch' insert:
    1. Persist RawData to get IDs.
    2. Link IDs to ProcessedData and persist.
    """

    # 1. Create and add Raw records
    raw_objs = [
        RawData(source=item["type"], payload=item["raw"])
        for item in batch_data
    ]
    db.add_all(raw_objs)
    
    # 2. Flush to the database to populate raw_objs[i].id
    # This does NOT end the transaction yet.
    await db.flush()

    # 3. Create Processed records using the newly generated IDs
    processed_objs = []
    for i, raw_item in enumerate(raw_objs):
        # The 'validated' data was passed along in our list
        validated = batch_data[i]["validated"]
        processed_objs.append(ProcessedData(
            raw_id=raw_item.id,
            external_id=validated.external_id,
            amount=validated.amount,
            currency=validated.currency
        ))

    db.add_all(processed_objs)
    
    # 4. Finalize the whole unit of work
    await db.commit()
    db.expunge_all()