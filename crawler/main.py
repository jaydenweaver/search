from src.crawler import Crawler
from src.processor import HTMLProcessor
from src.config import Config
from src.kafka_producer import KafkaProducer

def run_pipeline(config_path: str):
    config = Config(config_path)

    crawler = Crawler(config.crawler)
    pages = crawler.crawl()

    processor = HTMLProcessor(config.html)
    chunks = processor.process(pages)

    with KafkaProducer(config.kafka) as producer:
        producer.send(chunks)

if __name__ == "__main__":
    run_pipeline("config.yaml")