import os
import re
import yaml
from dataclasses import dataclass
from typing import Any, Dict

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
    group_id: str
    topic_pages_to_chunk: str
    topic_chunks_to_embed: str
    enable_auto_commit: bool
    auto_offset_reset: str


@dataclass
class ChunkConfig:
    chunk_size: int
    overlap: int
    min_chunk_length: int
    strip_scripts: bool
    clean_whitespace: bool
    include_metadata: bool


@dataclass
class WorkerConfig:
    batch_size: int
    retry_attempts: int
    retry_delay_seconds: int

class Config:
    def __init__(self, path: str):
        with open(path, "r") as f:
            raw = f.read()

        env_pattern = re.compile(r'\$\{([^}^{]+)\}')
        raw = env_pattern.sub(lambda m: os.getenv(m.group(1), ""), raw)

        data = yaml.safe_load(raw)

        self.database = DatabaseConfig(**data["database"])
        self.kafka = KafkaConfig(**data["kafka"])
        self.chunk = ChunkConfig(**data["chunk"])
        self.worker = WorkerConfig(**data["worker"])

    def __repr__(self) -> str:
        return (
            f"Config(database={self.database}, "
            f"kafka={self.kafka}, "
            f"chunk={self.chunk}, "
            f"worker={self.worker})"
        )
