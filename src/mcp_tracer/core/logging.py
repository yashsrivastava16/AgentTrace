"""
Logging configuration for the MCP server.

Sets up structured logging for AgentTrace.
"""

import logging

from mcp_tracer.core.config import settings


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    return logger
