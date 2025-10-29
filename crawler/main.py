from src.crawler import Crawler
from src.config import Config

def run_pipeline(config_path: str):
    crawler = Crawler()
    crawler.crawl()

if __name__ == "__main__":
    run_pipeline("config.yaml")