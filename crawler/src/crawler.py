import requests
from bs4 import BeautifulSoup
import logging

from src.config import Config
from src.kafka_producer import KafkaProducer
from src.db import Database

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Crawler:
    def __init__(self):
        config_path = "config.yaml"
        self.config = Config(config_path)

        self.db = Database(self.config.database)
        self.producer = KafkaProducer(self.config.kafka)

        self.visited = set()
        self.pages = []

    def crawl(self):
        to_visit = list(self.config.crawler.seed_urls)

        while to_visit and len(self.visited) < self.config.crawler.max_pages:
            url = to_visit.pop(0)

            if url in self.visited:
                continue

            try:
                html = self.fetch(url)
                if html:
                    # send to db + kafka
                    page_id = self.db.store_page(url, html)
                    self.producer.send_page_id(page_id)
                    self.visited.add(url)
                    logger.info(f"Crawled {url} ({len(self.visited)} / {self.config.crawler.max_pages})")

                    # find new links
                    for link in self.extract_links(html, url):
                        if link not in self.visited:
                            to_visit.append(link)
            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
            logger.info("Crawing complete.")
            return list(self.visited)


    def fetch(self, url):
        headers = {"User-Agent" : self.config.crawler.user_agent}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            return res.text
        
        logger.warning(f"Failed to fetch {url}, status {res.status_code}")
        return None
    
    def extract_links(self, html, base_url):
        soup = BeautifulSoup(html, "html.parser")
        links = set()

        # find <a> tags in html
        for a_tag in soup.find_all("a", href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            links.add(full_url)
        return links
        
