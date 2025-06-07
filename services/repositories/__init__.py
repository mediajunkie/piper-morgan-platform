import asyncpg
import os

class DatabasePool:
    """Singleton database connection pool"""
    _pool = None
    
    @classmethod
    async def get_pool(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                host="localhost",
                port=5432,
                user="piper",
                password=os.getenv("POSTGRES_PASSWORD", "dev_changeme"),
                database="piper_morgan",
                min_size=1,
                max_size=10
            )
        return cls._pool
    
    @classmethod
    async def close_pool(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
