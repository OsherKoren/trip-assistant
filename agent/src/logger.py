"""Logging configuration for the trip assistant agent using loguru.

This module sets up console logging with helpful debug information.
Import logger from this module to use throughout the application.

Example:
    from src.logger import logger

    logger.info("Processing query")
    logger.debug("State: {state}", state=state)
    logger.error("Failed to classify: {error}", error=str(e))
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

# Optional: Add more detailed logging for development
# Uncomment the following to enable DEBUG level logging:
# logger.remove()  # Remove the INFO handler first
# logger.add(
#     sys.stderr,
#     format=(
#         "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
#         "<level>{level: <8}</level> | "
#         "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
#         "<level>{message}</level> | "
#         "{extra}"
#     ),
#     level="DEBUG",
#     colorize=True,
# )

__all__ = ["logger"]
