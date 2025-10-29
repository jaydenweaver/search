class HTMLProcessor:
    def __init__(self, config):
        self.chunk_size = config.chunk_size
        self.overlap = config.overlap