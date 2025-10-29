from src.config import DatabaseConfig

class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config