import yaml
import os
import re
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

env_pattern = re.compile(r'\$\{([^}^{]+)\}')  # matches ${VAR_NAME}

class Config:
    def __init__(self, path):
        with open(path, "r") as f:
            raw = f.read()

        raw = env_pattern.sub(lambda m: os.getenv(m.group(1), ""), raw) # sub {VAR_NAME} with matching .env var
        data = yaml.safe_load(raw)

        self.crawler = CrawlerConfig(**data["crawler"])
        self.database = DatabaseConfig(**data["database"])
        self.kafka = KafkaConfig(**data["kafka"])
        self.html = HTMLConfig(**data["html"])
