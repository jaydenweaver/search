from kafka import KafkaProducer as BaseKafkaProducer
from json import dumps
from src.config import KafkaConfig
import logging

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self, config: KafkaConfig):
        self.config = config

        try:
            self.producer = BaseKafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                value_serializer=lambda v: dumps(v).encode("utf-8"),
                acks="all",
                linger_ms=10,
                retries=3
            )
            logger.info(f"Connected to Kafka at {self.config.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def send_page_id(self, page_id: int):
        """
        Publish a message containing the page_id
        to the 'pages_to_chunk' topic.
        """
        message = {"page_id": page_id}

        try:
            self.producer.send(self.config.topic_pages_to_chunk, value=message)
            logger.info(f"Sent page_id: {page_id} to {self.topic_pages_to_chunk}")
        except Exception as e:
            logger.error(f"Failed to send page_id {page_id}: {e}")
    
    def close(self):
        """ Flush and close the Kafka producer. """
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed.")        

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()