import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name):
    # Check if logger already exists
    if name in logging.root.manager.loggerDict:
        return logging.getLogger(name)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Only add handlers and print header if this is a new logger
    if not logger.handlers:
        console_handler = create_console_handler()
        file_handler = create_file_handler()
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        # Print run header only once
        if name == "__main__":  # Only print header for main logger
            logger.info("\n" + "#"*100)
            logger.info(f"#{'NEW RUN STARTED':^98}#")
            logger.info(f"#{datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^98}#")
            logger.info("#"*100 + "\n")
    
    return logger

def create_console_handler():
    """Create and configure console handler"""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create a custom formatter for console output
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message).500s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    return console_handler

def create_file_handler():
    """Create and configure rotating file handler"""
    current_date = datetime.now().strftime('%Y%m%d')
    filename = f'logs/feed_summarizer_{current_date}.log'
    
    file_handler = RotatingFileHandler(
        filename,
        maxBytes=5*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Use similar format to console but with milliseconds
    file_format = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message).500s',  # Limit message length
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    return file_handler

def log_section(logger, section_name):
    """Helper function to create visual separation between major operations"""
    logger.info("\n" + "-"*40)
    logger.info(f"Starting: {section_name}")
    logger.info("-"*40)

def log_summary(logger, section_name, success_count, total_count):
    """Helper function to log section summaries"""
    logger.info("\n" + "-"*40)
    logger.info(f"Completed: {section_name}")
    logger.info(f"Success: {success_count}/{total_count} ({(success_count/total_count)*100:.1f}%)")
    logger.info("-"*40 + "\n")