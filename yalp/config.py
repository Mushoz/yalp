"""Configuration handling for YALP.

Reads environment variables and provides defaults where appropriate.
"""

import os
from typing import Tuple


def get_host_port() -> Tuple[str, int]:
    """Return the host and port on which the server should listen.

    Environment variables:
    - ``YALP_HOST`` – default ``127.0.0.1``
    - ``YALP_PORT`` – default ``9333``
    """
    host = os.getenv("YALP_HOST", "127.0.0.1")
    port_str = os.getenv("YALP_PORT", "9333")
    try:
        port = int(port_str)
    except ValueError:
        raise ValueError(f"Invalid YALP_PORT value: {port_str!r}")
    return host, port


def get_upstream_base() -> str:
    """Return the upstream base URL.

    The ``YALP_BASE`` environment variable must be set. If it is missing,
    a ``RuntimeError`` is raised to make the mis‑configuration explicit.
    """
    base = os.getenv("YALP_BASE")
    if not base:
        raise RuntimeError("YALP_BASE environment variable is not set")
    # Ensure no trailing slash to simplify URL concatenation later.
    return base.rstrip("/")

