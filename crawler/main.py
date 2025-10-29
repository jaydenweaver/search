from src.crawler import Crawler
import logging

def run_pipeline(config_path: str):
    logging.basicConfig(level=logging.INFO)

    crawler = Crawler()
    crawler.crawl()

if __name__ == "__main__":
    run_pipeline("config.yaml")