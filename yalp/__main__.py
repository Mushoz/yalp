"""Entry point for the ``yalp`` console script.

It reads configuration from environment variables via :mod:`yalp.config`
and launches the FastAPI application defined in :mod:`yalp.proxy` using
``uvicorn``.
"""

import uvicorn

from .config import get_host_port
from .proxy import app


def main() -> None:
    """Start the proxy server.

    The host and port are obtained from ``YALP_HOST`` and ``YALP_PORT``
    environment variables, defaulting to ``127.0.0.1:9333`` as requested.
    """
    host, port = get_host_port()
    # ``uvicorn.run`` will block until the server stops.
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

