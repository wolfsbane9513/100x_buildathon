# report_generator/core/data/connection_manager.py
from typing import Dict, Any, Optional
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from aiomysql import create_pool
import asyncpg
import pandas as pd

class DatabaseConnectionManager:
    def __init__(self):
        self.connections = {}
    
    async def test_mongodb_connection(self, config: Dict[str, str]) -> bool:
        """Test MongoDB connection"""
        try:
            client = AsyncIOMotorClient(config['uri'])
            await client.admin.command('ping')
            return True
        except Exception as e:
            raise ConnectionError(f"MongoDB connection failed: {str(e)}")
        finally:
            client.close()
    
    async def test_mysql_connection(self, config: Dict[str, Any]) -> bool:
        """Test MySQL connection"""
        try:
            pool = await create_pool(**config)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
            return True
        except Exception as e:
            raise ConnectionError(f"MySQL connection failed: {str(e)}")
        finally:
            pool.close()
            await pool.wait_closed()
    
    async def test_postgresql_connection(self, config: Dict[str, Any]) -> bool:
        """Test PostgreSQL connection"""
        try:
            conn = await asyncpg.connect(**config)
            await conn.execute("SELECT 1")
            return True
        except Exception as e:
            raise ConnectionError(f"PostgreSQL connection failed: {str(e)}")
        finally:
            await conn.close()
    
    async def get_data_source(self, source_type: str, config: Dict[str, Any]) -> Any:
        """Get data source based on type and configuration"""
        if source_type == "mongodb":
            return await self._get_mongodb_data(config)
        elif source_type == "mysql":
            return await self._get_mysql_data(config)
        elif source_type == "postgresql":
            return await self._get_postgresql_data(config)
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")
    
    async def _get_mongodb_data(self, config: Dict[str, str]) -> pd.DataFrame:
        """Get data from MongoDB"""
        client = AsyncIOMotorClient(config['uri'])
        db = client[config['database']]
        collection = db[config['collection']]
        
        documents = []
        async for doc in collection.find():
            documents.append(doc)
        
        client.close()
        return pd.DataFrame(documents)
    
    async def _get_mysql_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Get data from MySQL"""
        pool = await create_pool(**config)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM your_table")  # Customize query
                rows = await cur.fetchall()
                columns = [desc[0] for desc in cur.description]
        
        pool.close()
        await pool.wait_closed()
        return pd.DataFrame(rows, columns=columns)
    
    async def _get_postgresql_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Get data from PostgreSQL"""
        conn = await asyncpg.connect(**config)
        rows = await conn.fetch("SELECT * FROM your_table")  # Customize query
        await conn.close()
        
        return pd.DataFrame([dict(row) for row in rows])