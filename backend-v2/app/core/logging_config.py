import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging():
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "backend-v2.log"

    fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
