"""
    The 'Contract' for all data sources.
    Requirement #1: Modular and pluggable input types.
"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any

class BaseIngestor(ABC):
    """
    Abstract base class defining the contract for all data ingestion sources.

    Implementations must expose an asynchronous streaming interface that yields
    records as dictionaries, independent of the underlying source type.
    """
    
    @abstractmethod
    async def stream_data(self, source: Any) -> AsyncGenerator[dict, None]:
        """
        Every ingestor MUST implement this as an async generator.
        This ensures the Orchestrator can 'pull' data without 
        knowing if it's a file, a DB, or a stream.
        """
        yield {}  # This is just a type hint for the interface