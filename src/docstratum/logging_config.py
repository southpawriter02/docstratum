"""Centralized logging configuration for DocStratum.

Provides a single entry point for configuring the application's logging
subsystem. All modules should use ``logging.getLogger(__name__)`` and
rely on this module to set up handlers, formatters, and levels.

Functions:
    setup_logging: Configure logging with structured format and environment-driven level.

Example:
    >>> from docstratum.logging_config import setup_logging
    >>> setup_logging()
    >>> import logging
    >>> logger = logging.getLogger(__name__)
    >>> logger.info("DocStratum initialized")

Research basis:
    FR-067 (all modules log key decisions at INFO level),
    NFR-006 (clear, actionable error messages).
    See RR-META-logging-standards.md for the full logging contract.
"""

import logging
import os

# Standard log format per RR-META-logging-standards.md §Log Format.
# Pipe-delimited fields: timestamp, level (left-aligned 8 chars),
# module:function:line, and message.
LOG_FORMAT: str = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
)
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger(__name__)


def setup_logging(level: str | None = None) -> None:
    """Configure logging for the DocStratum application.

    Reads the desired log level from the ``level`` parameter or the
    ``DOCSTRATUM_LOG_LEVEL`` environment variable, defaulting to INFO.
    Configures the root logger with a structured, pipe-delimited format
    suitable for both human reading and machine parsing.

    Args:
        level: Override log level (e.g., ``"DEBUG"``, ``"WARNING"``).
            If ``None``, reads from the ``DOCSTRATUM_LOG_LEVEL``
            environment variable, defaulting to ``"INFO"``.

    Example:
        >>> setup_logging()  # Uses env var or defaults to INFO
        >>> setup_logging("DEBUG")  # Forces DEBUG level
    """
    log_level = level or os.getenv("DOCSTRATUM_LOG_LEVEL", "INFO")

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )

    # Suppress noisy third-party loggers that may be installed
    # in downstream phases (v0.3.x-v0.5.x).
    for noisy_logger in ("httpx", "openai", "langchain"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    logger.info("Logging configured at %s level", log_level.upper())
