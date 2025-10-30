import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import json
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, config):
        self.config = config
        self.pool = None
        self._init_pool()
        self.init_schema()

    def _init_pool(self):
        """ Initialize a PostgreSQL connection pool. """
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=self.config.host,
                port=self.config.port,
                database=self.config.name,
                user=self.config.user,
                password=self.config.password
            )
            logger.info(f"PostgreSQL connection pool established at {self.config.host}:{self.config.port}")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    def init_schema(self):
        """ Create the 'chunks' table if it doesn't exist. """
        query = """
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                page_id INT REFERENCES pages(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
                logger.info("Database schema initialized successfully.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to initialize schema: {e}")
            raise
        finally:
            self.pool.putconn(conn)

    def get_page_by_id(self, page_id: int):
        query = "SELECT * FROM pages WHERE id = %s;"
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (page_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch page {page_id}: {e}")
            return None
        finally:
            self.pool.putconn(conn)

    def insert_chunk(self, page_id: int, content: str, metadata: dict = None) -> int:
        """ Insert a chunk into the 'chunks' table and return its ID. """
        query = """
            INSERT INTO chunks (page_id, content, metadata)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                metadata_json = json.dumps(metadata) if metadata else None
                cursor.execute(query, (page_id, content, metadata_json))
                chunk_id = cursor.fetchone()["id"]
                conn.commit()
                logger.debug(f"Inserted chunk {chunk_id} for page {page_id}")
                return chunk_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to insert chunk for page {page_id}: {e}")
            return None
        finally:
            self.pool.putconn(conn)

    def close(self):
        """ Close all connections in the pool. """
        if self.pool:
            self.pool.closeall()
            logger.info("PostgreSQL connection pool closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
