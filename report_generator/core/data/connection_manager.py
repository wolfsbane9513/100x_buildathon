from typing import Dict, Any, Optional, List, Union
import logging
import asyncio
import json
import pandas as pd

# Database imports
import pymongo
import mysql.connector
from motor.motor_asyncio import AsyncIOMotorClient
import aiomysql
import asyncpg
from mysql.connector import Error as MySQLError
from pymongo.errors import ConnectionError as MongoConnectionError

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class ConnectionManager:
    def __init__(self):
        """Initialize the connection manager"""
        self.connections: Dict[str, Any] = {}
        self._setup_logging()
        self.supported_databases = {
            'mongodb': self._connect_mongodb,
            'mysql': self._connect_mysql,
            'postgresql': self._connect_postgresql
        }
    
    def _setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler('database.log')
        
        # Create formatters and add it to handlers
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(log_format)
        file_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    async def create_connection(self, db_type: str, config: Dict[str, Any]) -> bool:
        """
        Create a new database connection
        
        Args:
            db_type: Type of database ('mongodb', 'mysql', 'postgresql')
            config: Connection configuration dictionary
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if db_type not in self.supported_databases:
                raise DatabaseError(f"Unsupported database type: {db_type}")
            
            # Check if connection already exists
            if db_type in self.connections:
                self.logger.warning(f"Connection to {db_type} already exists")
                return True
            
            # Create new connection
            connect_func = self.supported_databases[db_type]
            return await connect_func(config)
            
        except Exception as e:
            self.logger.error(f"Error creating connection to {db_type}: {str(e)}")
            raise DatabaseError(f"Connection failed: {str(e)}")

    async def _connect_mongodb(self, config: Dict[str, Any]) -> bool:
        """Create MongoDB connection"""
        try:
            required_keys = ['uri', 'database']
            if not all(key in config for key in required_keys):
                raise DatabaseError("Missing required MongoDB configuration")
            
            client = AsyncIOMotorClient(config['uri'])
            await client.admin.command('ping')
            
            self.connections['mongodb'] = {
                'client': client,
                'database': client[config['database']],
                'config': config
            }
            
            self.logger.info("MongoDB connection established successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"MongoDB connection error: {str(e)}")
            raise DatabaseError(f"MongoDB connection failed: {str(e)}")

    async def _connect_mysql(self, config: Dict[str, Any]) -> bool:
        """Create MySQL connection"""
        try:
            required_keys = ['host', 'user', 'password', 'database']
            if not all(key in config for key in required_keys):
                raise DatabaseError("Missing required MySQL configuration")
            
            # Test connection first
            test_conn = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
            test_conn.close()
            
            # Create connection pool
            pool = await aiomysql.create_pool(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                db=config['database'],
                autocommit=True,
                pool_recycle=3600,  # Recycle connections after 1 hour
                maxsize=10          # Maximum number of connections
            )
            
            self.connections['mysql'] = {
                'pool': pool,
                'config': config
            }
            
            self.logger.info("MySQL connection established successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"MySQL connection error: {str(e)}")
            raise DatabaseError(f"MySQL connection failed: {str(e)}")

    async def _connect_postgresql(self, config: Dict[str, Any]) -> bool:
        """Create PostgreSQL connection"""
        try:
            required_keys = ['host', 'user', 'password', 'database']
            if not all(key in config for key in required_keys):
                raise DatabaseError("Missing required PostgreSQL configuration")
            
            # Test connection
            conn = await asyncpg.connect(**config)
            await conn.execute('SELECT 1')
            await conn.close()
            
            self.connections['postgresql'] = {
                'config': config,
                'pool': await asyncpg.create_pool(**config)
            }
            
            self.logger.info("PostgreSQL connection established successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL connection error: {str(e)}")
            raise DatabaseError(f"PostgreSQL connection failed: {str(e)}")

    async def execute_query(self, db_type: str, query: str) -> pd.DataFrame:
        """
        Execute query and return results as DataFrame
        
        Args:
            db_type: Type of database
            query: Query string
            
        Returns:
            pandas.DataFrame: Query results
        """
        if db_type not in self.connections:
            raise DatabaseError(f"No connection exists for {db_type}")

        try:
            if db_type == "mongodb":
                results = await self._execute_mongodb_query(query)
            elif db_type == "mysql":
                results = await self._execute_mysql_query(query)
            elif db_type == "postgresql":
                results = await self._execute_postgresql_query(query)
            else:
                raise DatabaseError(f"Unsupported database type: {db_type}")
            
            # Convert results to DataFrame
            return pd.DataFrame(results)
            
        except Exception as e:
            self.logger.error(f"Query execution error: {str(e)}")
            raise DatabaseError(f"Query execution failed: {str(e)}")

    async def _execute_mongodb_query(self, query: str) -> List[Dict]:
        """Execute MongoDB query"""
        try:
            db = self.connections['mongodb']['database']
            # Parse the query string to MongoDB query
            query_dict = json.loads(query) if isinstance(query, str) else query
            cursor = db.find(query_dict)
            results = await cursor.to_list(length=None)
            return results
        except Exception as e:
            self.logger.error(f"MongoDB query error: {str(e)}")
            raise

    async def _execute_mysql_query(self, query: str) -> List[tuple]:
        """Execute MySQL query"""
        try:
            pool = self.connections['mysql']['pool']
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query)
                    results = await cur.fetchall()
                    # Get column names
                    columns = [d[0] for d in cur.description]
                    # Convert to list of dicts
                    return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            self.logger.error(f"MySQL query error: {str(e)}")
            raise

    async def _execute_postgresql_query(self, query: str) -> List[Dict]:
        """Execute PostgreSQL query"""
        try:
            pool = self.connections['postgresql']['pool']
            async with pool.acquire() as conn:
                results = await conn.fetch(query)
                return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"PostgreSQL query error: {str(e)}")
            raise

    async def test_connection(self, db_type: str) -> bool:
        """Test if database connection is alive"""
        if db_type not in self.connections:
            return False
            
        try:
            if db_type == "mongodb":
                await self.connections[db_type]['client'].admin.command('ping')
            elif db_type == "mysql":
                async with self.connections[db_type]['pool'].acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("SELECT 1")
            elif db_type == "postgresql":
                async with self.connections[db_type]['pool'].acquire() as conn:
                    await conn.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed for {db_type}: {str(e)}")
            return False

    async def close_connection(self, db_type: str):
        """Close specific database connection"""
        if db_type in self.connections:
            try:
                if db_type == "mongodb":
                    self.connections[db_type]['client'].close()
                elif db_type == "mysql":
                    self.connections[db_type]['pool'].close()
                    await self.connections[db_type]['pool'].wait_closed()
                elif db_type == "postgresql":
                    await self.connections[db_type]['pool'].close()
                del self.connections[db_type]
                self.logger.info(f"Closed connection to {db_type}")
            except Exception as e:
                self.logger.error(f"Error closing {db_type} connection: {str(e)}")

    async def close_all_connections(self):
        """Close all database connections"""
        for db_type in list(self.connections.keys()):
            await self.close_connection(db_type)
        self.logger.info("All connections closed")

    def get_connection_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status of all connections"""
        status = {}
        for db_type in self.connections:
            try:
                if db_type == "mongodb":
                    status[db_type] = {
                        'connected': True,
                        'database': self.connections[db_type]['config']['database'],
                        'host': self.connections[db_type]['config']['uri'].split('@')[-1].split('/')[0]
                    }
                else:
                    status[db_type] = {
                        'connected': True,
                        'database': self.connections[db_type]['config']['database'],
                        'host': self.connections[db_type]['config']['host']
                    }
            except Exception:
                status[db_type] = {'connected': False}
        return status

    def get_supported_databases(self) -> List[str]:
        """Get list of supported database types"""
        return list(self.supported_databases.keys())