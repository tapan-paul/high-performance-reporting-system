"""
This module defines the data schema for incoming records using Pydantic.
The DataRecord model includes validation rules and transformation logic to ensure data integrity.
Example usage:
    from app.schemas.data_schema import DataRecord

    try:
        record = DataRecord(
            external_id="12345",
            amount=150.00,
            currency="usd",
            source_channel="API"
        )
        print(record)
    except ValidationError as e:
        print("Validation error:", e)
"""
from datetime import datetime
from pydantic import Field, BaseModel, field_validator
from app.core.config import settings


class DataRecord(BaseModel):
    """
    DataRecord model represents the structure of incoming data records with validation.
    Fields:
    - external_id: Unique identifier from the source system (string, required)
    - amount: Transaction amount (float, required, must be greater than zero)
    - currency: ISO 4217 currency code (string, required, must be 3 letters
    - source_channel: Source channel of the transaction (string, required)
    - timestamp: Timestamp of the transaction (datetime, optional, defaults to current time)
    """
    external_id: str = Field(..., description="Unique ID from the source system")
    amount: float = Field(..., gt=0, description="Transaction amount must be positive")
    currency: str = Field(default="USD")
    source_channel: str = Field(..., description="e.g., CSV, Kafka, etc.")
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, value: str) -> str:
        """
        check for validate currencies
        """
        if value.upper() not in settings.ALLOWED_CURRENCIES:
            raise ValueError(f"Currency {value} is not supported by our system")
        return value.upper()
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value : float) -> int:
        """
        Amount cant be non-positive
        
        :param cls: Description
        :param value: Description
        """
        if value <= 0:
            raise ValueError('Amount must be greater than zero')
        return value
    
    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value) -> datetime:
        """
        Timestamp isnt in the future
        
        :param cls: Description
        :param value: Description
        """
        if value and value > datetime.now():
            raise ValueError('Timestamp cannot be in the future')
        return value