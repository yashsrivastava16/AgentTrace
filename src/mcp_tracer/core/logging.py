"""
Internal logger for AgentTrace.
"""
import logging
import sys

from mcp_tracer.core.config import settings


def _setup_logger() -> logging.Logger:
    log = logging.getLogger("agenttrace")
    log.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    log.addHandler(handler)
    return log


logger = _setup_logger()