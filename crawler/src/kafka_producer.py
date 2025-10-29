from src.config import KafkaConfig

class KafkaProducer:
    def __init__(self, config: KafkaConfig):
        self.config = config
    