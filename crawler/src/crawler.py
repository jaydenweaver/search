
class Crawler:
    def __init__(self, config):
        self.seed_urls = config.seed_urls
        self.max_pages = config.max_pages
        self.max_depth = config.max_depth
        self.user_agent = config.user_agent
        self.delay_seconds = config.delay_seconds

        self.visited = set()
        self.pages = []
