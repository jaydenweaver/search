import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        """ Open the connection to the PostgreSQL database """
        if self.conn is None:
            self.conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                dbname=self.config.name,
                user=self.config.user,
                password=self.config.password
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def get_page_by_id(self, page_id: int):
        self.connect()
        query = "SELECT * FROM pages WHERE id = %s;"
        self.cursor.execute(query, (page_id,))
        return self.cursor.fetchone()

    def insert_chunk(self, page_id: int, content: str, metadata: dict = None) -> int:
        """ Inserts a chunk into the 'chunks' table and returns its ID. """
        self.connect()
        metadata_json = json.dumps(metadata) if metadata else None
        
        query = """
            INSERT INTO chunks (page_id, content, metadata)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        
        self.cursor.execute(query, (page_id, content, metadata_json))
        self.conn.commit()
        chunk_id = self.cursor.fetchone()["id"]
        logger.debug(f"Inserted chunk {chunk_id} for page {page_id}")
        return chunk_id
    
    def close(self):
        """Close the DB connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
