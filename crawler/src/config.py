import yaml
from dataclasses import dataclass

@dataclass
class CrawlerConfig:
    seed_urls: list[str]
    max_pages: int
    max_depth: int
    user_agent: str
    delay_seconds: float

@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str

@dataclass
class KafkaConfig:
    bootstrap_servers: str
    topic_chunks_to_embed: str

@dataclass
class HTMLConfig:
    chunk_size: int
    overlap: int

class Config:
    def __init__(self, path):
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        self.crawler = CrawlerConfig(**data["crawler"])
        self.database = DatabaseConfig(**data["database"])
        self.kafka = KafkaConfig(**data["kafka"])
        self.html = HTMLConfig(**data["html"])
