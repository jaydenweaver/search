import logging
from kafka import KafkaProducer as KafkaProducerClient
import json
from src.config import KafkaConfig

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.producer = KafkaProducerClient(
            bootstrap_servers=self.config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def send_chunk_id(self, chunk_id: int):
        """ Publish a message containing the chunk_id to the 'chunks_to_embed' topic. """
        message = {"chunk_id": chunk_id}

        try:
            self.producer.send(self.config.topic_chunks_to_embed, value=message)
            logger.info(f"Sent chunk_id={chunk_id} to topic '{self.config.topic_chunks_to_embed}'")
        except Exception as e:
            logger.error(f"Failed to send chunk_id {chunk_id}: {e}")

    def close(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
