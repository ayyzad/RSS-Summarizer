import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name):
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Rotating file handler - 5MB per file, keep 5 backup files
    file_handler = RotatingFileHandler(
        f'logs/feed_summarizer.log',
        maxBytes=5*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    # Create formatters
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Add formatters to handlers
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger