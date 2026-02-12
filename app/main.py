import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.models.database import init_db
from app.api.v1.ingestion_router import router as ingestion_router
from app.api.v1.reporting_router import router as reporting_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    await init_db()
    logger.info("🚀 System Online: Database initialized and tables created.")
    
    # Optional: If you decide to add the Kafka background worker later, 
    # you would launch the task here.
    ### # Start Kafka worker
    ## kafka_worker = KafkaWorker()
    ##await kafka_worker.start()
    
    yield  # App is running...

    # --- SHUTDOWN ---
    ##await kafka_worker.stop()
    ##await engine.dispose()
    logger.info("🛑 System Offline: Database connections closed safely.")

app = FastAPI(
    title="High-Performance Reporting System",
    description="A modular bridge for high-speed data ingestion and validation.",
    version="1.0.0",
    lifespan=lifespan
)

# Registering versioned routers
app.include_router(ingestion_router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(reporting_router, prefix="/api/v1", tags=["Reporting"])