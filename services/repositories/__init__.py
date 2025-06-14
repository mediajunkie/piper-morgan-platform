import asyncpg
import os

class DatabasePool:
    """Singleton database connection pool"""
    _pool = None
    
    @classmethod
    async def get_pool(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                user=os.getenv("POSTGRES_USER", "piper"),
                password=os.getenv("POSTGRES_PASSWORD", "dev_changeme"),
                database=os.getenv("POSTGRES_DB", "piper_morgan"),
                min_size=1,
                max_size=10
            )
        return cls._pool
    
    @classmethod
    async def close_pool(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None