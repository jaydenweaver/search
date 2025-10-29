from src.config import DatabaseConfig

class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config
    
    def store_page(url: str, html: str) -> int:
        """
        returns page_id of stored page
        """
        pass