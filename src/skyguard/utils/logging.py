from __future__ import annotations

import logging


def get_logger(name: str = "skyguard") -> logging.Logger:
    """Return the shared application logger without configuring global handlers."""
    return logging.getLogger(name)