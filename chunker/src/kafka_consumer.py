import json
import logging
from kafka import KafkaConsumer
from src.config import KafkaConfig

logger = logging.getLogger(__name__)


class KafkaConsumerWrapper:
    def __init__(self, config: KafkaConfig, topic: str):
        self.topic = topic
        self.config = config

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=config.bootstrap_servers,
            group_id=config.group_id,
            enable_auto_commit=config.enable_auto_commit,
            auto_offset_reset=config.auto_offset_reset,
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )

        logger.info(f"KafkaConsumer connected to topic: {topic}")

    def consume(self):
        """ Generator that yields messages from the Kafka topic. """
        for message in self.consumer:
            yield message

    def close(self):
        if self.consumer:
            self.consumer.close()
            logger.info(f"KafkaConsumer for topic {self.topic} closed.")
