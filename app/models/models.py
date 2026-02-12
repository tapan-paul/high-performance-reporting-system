from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    ForeignKey,
    Float,
    Text
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class RawData(Base):
    """
    Stores raw, immutable data exactly as received from the source.
    Used for traceability, auditing, and reprocessing.
    """
    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True)
    source = Column(String, index=True, nullable=False)
    payload = Column(JSON, nullable=False)
    received_at = Column(DateTime(timezone=True), default=datetime.now)

    processed_records = relationship("ProcessedData", back_populates="raw")


class ProcessedData(Base):
    """
    Stores validated and normalized data derived from RawData.
    Used for reporting and downstream analytics.
    """
    __tablename__ = "processed_data"

    id = Column(Integer, primary_key=True)
    raw_id = Column(Integer, ForeignKey("raw_data.id"), nullable=False)

    external_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)

    status = Column(String, default="PROCESSED")
    processed_at = Column(DateTime(timezone=True), default=datetime.now)

    raw = relationship("RawData", back_populates="processed_records")

class IngestionError(Base):
    """
    Requirement #2 & #3: Persistence of validation failures for auditing.
    """
    __tablename__ = "ingestion_errors"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50))     # e.g., 'csv' or 'json'
    source_path = Column(String(255))    # The filename
    raw_content = Column(Text)           # The actual bad row/object string
    error_message = Column(Text)         # The Pydantic validation error
    created_at = Column(DateTime, default=datetime.now)