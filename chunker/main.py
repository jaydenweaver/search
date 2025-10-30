from src.chunker import Chunker
import logging

def run_pipeline():
    logging.basicConfig(level=logging.INFO)

    chunker = Chunker()
    chunker.process_queue()

if __name__ == "__main__":
    run_pipeline()