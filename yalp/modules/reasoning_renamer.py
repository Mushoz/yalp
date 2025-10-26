"""Reasoning renamer module.

Provides a small, reusable class that inspects an ``httpx.Response`` and, if
the payload is JSON, renames any ``reasoning_content`` fields to ``reasoning``.
It returns a ``fastapi.StreamingResponse`` ready to be sent back to the
client. Non‑JSON responses are streamed unchanged.
"""

import json
import io
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from httpx import Response


class ReasoningRenamer:
    """Rename ``reasoning_content`` → ``reasoning`` in JSON responses.

    The class is deliberately lightweight – it contains no proxy‑specific
    logic and can be imported wherever a response needs this transformation.
    """

    async def __call__(self, resp: Response) -> StreamingResponse:
        """Transform the response if JSON, otherwise stream unchanged.

        Parameters
        ----------
        resp: httpx.Response
            The upstream response object.
        """
        # Attempt to read the full body and parse as JSON regardless of headers.
        raw_body = await resp.aread()
        try:
            data = json.loads(raw_body)
        except Exception:
            # Not JSON – stream the original raw bytes.
            response_headers = dict(resp.headers)
            response_headers["content-length"] = str(len(raw_body))
            background = BackgroundTask(resp.aclose)
            return StreamingResponse(
                io.BytesIO(raw_body),
                status_code=resp.status_code,
                headers=response_headers,
                background=background,
            )
        # Rename top‑level field.
        if isinstance(data, dict) and "reasoning_content" in data:
            data["reasoning"] = data.pop("reasoning_content")
        # Rename nested field inside choices → message.
        if isinstance(data, dict):
            for choice in data.get("choices", []):
                if isinstance(choice, dict):
                    msg = choice.get("message", {})
                    if isinstance(msg, dict) and "reasoning_content" in msg:
                        msg["reasoning"] = msg.pop("reasoning_content")
        body_bytes = json.dumps(data).encode("utf-8")
        response_headers = dict(resp.headers)
        response_headers["content-length"] = str(len(body_bytes))
        background = BackgroundTask(resp.aclose)
        return StreamingResponse(
            io.BytesIO(body_bytes),
            status_code=resp.status_code,
            headers=response_headers,
            background=background,
        )
