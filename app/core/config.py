"""
Main config location and and be overridden per environment
- For local development, create a .env file with the following content eg:
    ALLOWED_CURRENCIES=["USD","EUR", "GBP", "AUD"]
- For production, set environment variables directly or use a secrets manager.
Example usage:
    from app.core.config import settings
    
    print(settings.ALLOWED_CURRENCIES)
    print(settings.DATABASE_URL)
    print(settings.APP_NAME)
  
"""
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
        Settings class to hold configuration values for the application 
    """

    # Requirement #1: Scalable Configuration
    # You can override these in a .env file: ALLOWED_CURRENCIES=["USD","EUR", "GBP", "AUD"]
    ALLOWED_CURRENCIES: List[str] = ["USD", "EUR", "GBP", "AUD"]

    BATCH_SIZE :int = 10000
    DATABASE_URL: str = "sqlite+aiosqlite:///./reporting.db?timeout=30"
    APP_NAME: str = "Reporting System API"
    FILE_CSV: str = "csv"
    FILE_JSON: str = "json"
    FILE_XLSX: str = "xlsx"
    REPORT_FORMATS: dict[str,str] = {
        "csv": "text/csv",
        "json": "application/json",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    # kafka 
    KAFKA_TOPIC: str = "topic"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "reporting-consumer-group"

    class Config:
        """
            local file 
        """
        env_file = ".env"

# Create a single instance to be used across the app
settings = Settings()
