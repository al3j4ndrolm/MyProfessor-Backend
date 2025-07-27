import logging
from .config import configure_logging

# Configure logging when the module is imported
configure_logging()

# Create and export a logger instance that can be used directly
logger = logging.getLogger(__name__)

# Export the logger instance so it can be used as: import logger; logger.info("message")
__all__ = ['logger']