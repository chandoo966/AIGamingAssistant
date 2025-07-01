import logging
import logging.config
import sys
from typing import Optional
from .config import LOG_CONFIG

def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Set up and return a logger instance"""
    logging.config.dictConfig(LOG_CONFIG)
    return logging.getLogger(name)

class GameAssistantLogger:
    def __init__(self, name: str):
        self.logger = setup_logger(name)
        
    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)
        
    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)
        
    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)
        
    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)
        
    def critical(self, message: str, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)
        
    def exception(self, message: str, *args, **kwargs):
        self.logger.exception(message, *args, **kwargs) 