from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.models import Base  # Crucial: Import the Base where your tables are defined
from app.core.config import settings
from sqlalchemy import event

engine = create_async_engine(settings.DATABASE_URL)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# This event listener turns on WAL mode every time a connection is made
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=30000") # 30 seconds
    cursor.close()
    
async def init_db():
    """
    Creates all tables in the database.
    Requirement #3: Persistence layer setup.
    """
    async with engine.begin() as conn:
        # This looks at every class inheriting from 'Base' and creates the table
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session