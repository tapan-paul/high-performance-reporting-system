import logging
import json
import asyncio
from aiokafka import AIOKafkaConsumer
from app.core.orchestrator import DataOrchestrator
from app.models.database import async_session_factory
from app.core.config import settings

logger = logging.getLogger(__name__)

class KafkaWorker:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_GROUP_ID,
            enable_auto_commit=False,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        self.orchestrator = DataOrchestrator()
        self._task = None
        self._running = False

    async def start(self):
        await self.consumer.start()
        self._running = True
        self._task = asyncio.create_task(self._consume())
        logger.info("Kafka worker started")

    async def _consume(self):
        try:
            async for message in self.consumer:
                async with async_session_factory() as db:
                    await self.orchestrator.process(
                        db=db,
                        raw_data=message.value,
                        source_type="kafka",
                        source_ref=message.topic,
                    )

                await self.consumer.commit()
        except Exception as e:
            logger.exception("Kafka worker crashed: %s", e)

    async def stop(self):
        self._running = False
        await self.consumer.stop()
        logger.info("Kafka worker stopped")
