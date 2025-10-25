"""Core proxy implementation.

Provides a :class:`fastapi.FastAPI` instance that forwards any incoming
HTTP request to the upstream service defined by ``YALP_BASE``.

The forwarding logic is intentionally simple: it copies the method, path,
query string, headers (excluding ``host``), and body to the upstream URL
using an :class:`httpx.AsyncClient`. The response from the upstream is then
returned to the original client preserving status code, headers, and body.
"""

from fastapi import FastAPI, Request, Response
import httpx

from .config import get_upstream_base

app = FastAPI(title="YALP Proxy")

# A single shared client for all requests – it will be closed automatically
# when the FastAPI lifespan ends (uvicorn will handle the event loop).
client = httpx.AsyncClient()


def _strip_host_header(headers: dict) -> dict:
    """Remove ``host`` header to let httpx set the correct upstream host.

    ``httpx`` automatically adds a ``host`` header based on the request URL.
    If we forward the original ``host`` header it would point to the proxy
    itself, which could confuse upstream services.
    """
    return {k: v for k, v in headers.items() if k.lower() != "host"}


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy(full_path: str, request: Request):
    """Catch‑all route that forwards the request to the upstream service.

    The ``full_path`` variable captures the entire path portion of the URL.
    Query parameters are retained automatically via ``request.url``.
    """
    upstream_base = get_upstream_base()
    # Build the full upstream URL preserving the original path and query
    upstream_url = f"{upstream_base}/{full_path}" + (f"?{request.url.query}" if request.url.query else "")

    # Read body (can be None for GET/HEAD)
    body = await request.body()

    # Prepare headers, stripping the Host header
    headers = _strip_host_header(dict(request.headers))

    # Forward the request
    resp = await client.request(
        method=request.method,
        url=upstream_url,
        headers=headers,
        content=body,
        timeout=30.0,
    )

    # Build FastAPI response preserving status, headers, and body
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))

