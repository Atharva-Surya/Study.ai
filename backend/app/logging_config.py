import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "logs/app.log")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB
    backup = int(os.getenv("LOG_BACKUP_COUNT", 5))

    # Ensure log dir exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%S%z"

    root = logging.getLogger()
    root.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    root.addHandler(ch)

    # Rotating file handler
    fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    root.addHandler(fh)

    # Reduce noisy third-party loggers if desired
    logging.getLogger("sqlalchemy.engine").setLevel("WARNING")
    logging.getLogger("uvicorn.access").setLevel("INFO")
    logging.getLogger("uvicorn.error").setLevel("INFO")