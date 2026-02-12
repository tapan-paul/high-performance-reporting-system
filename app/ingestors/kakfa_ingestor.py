"""
Kafka Ingestor Module
-------------------

 Current implementation is a mock for architectural demonstration. Production requires aiokafka and a background worker.
The Refactor: move the Kafka logic out of your v1/reporting_router.py and v1/ingestion_router.py and into the FastAPI Lifespan


"""
import asyncio
from typing import AsyncIterator, Dict, Any
import logging
from app.ingestors.base_ingestor import BaseIngestor


class KafkaIngestor(BaseIngestor):
    """
    Ingestor for Kafka topics. Implements the BaseIngestor contract.
    
    Usage:
        kafka_ingestor = KafkaIngestor()
        async for message in kafka_ingestor.stream_data('my_kafka_topic'):
            print(message)
    """
    async def stream_data(self, source: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Mocking a Kafka Consumer. In production, this would wrap aiokafka.
        """
        logging.info('Subscribing to Kafka Topic %s:', source)
        
        # Simulate an infinite stream of real-time events
        while True:
            await asyncio.sleep(1) # Simulate network lag
            # Mock data coming off the wire
            yield {
                "external_id": "KAFKA-123",
                "amount": 99.99,
                "currency": "USD",
                "source_channel": "KAFKA_PROD"
            }