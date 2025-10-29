class KafkaProducer:
    def __init__(self, config):
        self.bootstrap_servers = config.bootstrap_servers
        self.topic_chunks_to_embed = config.topic_chunks_to_embed
    