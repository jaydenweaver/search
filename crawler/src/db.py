from src.config import DatabaseConfig
import psycopg2
from psycopg2 import pool
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, config: DatabaseConfig):
        """ Initialise PostgreSQL connection pool. """
        self.config = config

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
            logger.info(f"Connection to PostgreSQL at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
        
        self._init_schema()

    def _init_schema(self):
        """ Create the 'pages' table if it doesn't exist. """

        query = """
        CREATE TABLE IF NOT EXISTS pages (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE,
            html TEXT,
            crawled_at TIMESTAMP DEFAULT NOW()
        );
        """

        conn = self.pool.getconn()
        try:
            with conn.cursor() as c:
                c.execute(query)
                conn.commit()
        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            conn.rollback()
        finally:
            self.pool.putconn(conn)
    
    def store_page(self, url: str, html: str) -> int:
        """
            Inserts a crawled page into the database and returns its page ID.
            If the page already exists, it updates the HTML and timestamp.
        """
        
        query = """
            INSERT INTO pages (url, html, crawled_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (url)
            DO UPDATE SET html = EXCLUDED.html, crawled_at = EXCLUDED.crawled_at
            RETURNING id;
        """

        conn = self.pool.getconn()
        try:
            with conn.cursor() as c:
                c.execute(query, (url, html, datetime.now))
                page_id = c.fetchone()[0]
                conn.commit()
                logger.info(f"Stored page: {url} (id: {page_id})")
                return page_id
        except Exception as e:
            logger.error(f"Failed to store page {url}: {e}")
            conn.rollback()
            return None
        finally:
            self.pool.putconn(conn)
    
    def close(self):
        """ Close all connections """
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()