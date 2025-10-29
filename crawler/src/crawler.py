from src.config import CrawlerConfig

class Crawler:
    def __init__(self, config: CrawlerConfig):
        self.config = config

        self.visited = set()
        self.pages = []
