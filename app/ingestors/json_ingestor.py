import json
import aiofiles
from app.ingestors.base_ingestor import BaseIngestor

class JSONIngestor(BaseIngestor):
    async def stream_data(self, source: str):
        async with aiofiles.open(source, mode='r') as f:
            async for line in f:
                if line.strip():
                    yield json.loads(line)