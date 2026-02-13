"""Logging configuration for the trip assistant API using loguru.

This module sets up console logging with helpful debug information.
Import logger from this module to use throughout the application.

Example:
    from app.logger import logger

    logger.info("Processing request")
    logger.debug("Request: {request}", request=request)
    logger.error("Failed to process: {error}", error=str(e))
"""

import sys

from loguru import logger

# Remove default handler
logger.remove()

# Add console handler with custom format
logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)

__all__ = ["logger"]
