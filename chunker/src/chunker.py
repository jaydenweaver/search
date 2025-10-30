import logging
import re
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from src.config import Config
from src.db import Database
from src.kafka_consumer import KafkaConsumerWrapper
from src.kafka_producer import KafkaProducer

logger = logging.getLogger(__name__)


class Chunker:
    def __init__(self, config: Config):
        self.config = config
        self.db = Database(config.database)
        self.producer = KafkaProducer(config.kafka)
        self.consumer = KafkaConsumerWrapper(
            config.kafka,
            topic=config.kafka.topic_pages_to_chunk
        )

        self.strip_scripts = config.html.strip_scripts
        self.clean_whitespace = config.html.clean_whitespace
        self.include_metadata = config.html.include_metadata

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.html.chunk_size,
            chunk_overlap=config.html.overlap,
            length_function=len
        )

    def clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        if self.strip_scripts:
            for tag in soup(["script", "style"]):
                tag.decompose()
        text = soup.get_text(separator=" ")
        if self.clean_whitespace:
            text = re.sub(r"\s+", " ", text).strip()
        return text

    def process_page(self, page_id: int):
        page = self.db.get_page_by_id(page_id)
        if not page:
            logger.warning(f"Page ID {page_id} not found in database")
            return

        html_content = page["content"]

        cleaned_text = self.clean_html(html_content)

        # split into chunks
        doc_metadata = {"url": page["url"]} if self.include_metadata else {}
        doc = Document(page_content=cleaned_text, metadata=doc_metadata)
        chunks = self.splitter.split_documents([doc])

        # insert chunks to db
        chunk_ids = []
        for chunk_doc in chunks:
            chunk_id = self.db.insert_chunk(
                page_id=page_id,
                content=chunk_doc.page_content,
                metadata=chunk_doc.metadata
            )
            chunk_ids.append(chunk_id)

        logger.info(f"Inserted {len(chunk_ids)} chunks for page_id={page_id}")

        # send to embedding queue
        for chunk_id in chunk_ids:
            self.producer.send_chunk_id(chunk_id)

    def run(self):
        logger.info("Chunker service started.")
        try:
            for message in self.consumer.consume():
                page_id = message.value.get("page_id")
                if page_id is not None:
                    self.process_page(page_id)
                else:
                    logger.warning(f"Received message without page_id: {message.value}")
        except KeyboardInterrupt:
            logger.info("Chunker service stopped by user.")
        finally:
            self.consumer.close()
            self.producer.close()

