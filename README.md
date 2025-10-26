# YALP – Yet Another LLM Proxy

YALP is a tiny **FastAPI** based HTTP proxy that forwards any request to an
up‑stream LLM service (e.g. OpenAI, Anthropic, etc.).  It rewrites the
`reasoning_content` field in JSON payloads to `reasoning` – a convenience used by
some downstream tools – and streams the response back to the client unchanged
otherwise.

## Features

- Minimal, async implementation based on **FastAPI**, **uvicorn**, and **httpx**.
- Automatic environment‑variable configuration for host, port and upstream URL.
- Transparent proxying – all HTTP methods, query strings, headers (except `host`)
  and body are forwarded.
- Built‑in response transformer (`ReasoningRenamer`) that safely mutates JSON
  responses while preserving status codes and headers.

## Installation

YALP can be installed from the source repository or from a built distribution.
It requires Python 3.9+.

```bash
# From source (editable install)
pip install -e .

# Or a regular install
pip install .
```

The project also ships a `uv.lock` file; if you prefer **uv** you can install
with:

```bash
uv pip install .
```

## Configuration

Configuration is done via environment variables:

| Variable      | Description                                 | Default |
|---------------|---------------------------------------------|---------|
| `YALP_HOST`  | Interface address the proxy binds to.       | `127.0.0.1` |
| `YALP_PORT`  | TCP port the proxy listens on.              | `9333` |
| `YALP_BASE`  | **Required.** Base URL of the upstream LLM service (e.g. `https://api.openai.com/v1`). |

The proxy will raise a `RuntimeError` at start‑up if `YALP_BASE` is not set.

## Running the Proxy

After installing, a console script `yalp` is provided:

```bash
# Set the required upstream URL
export YALP_BASE="https://api.openai.com/v1"

# Optional custom host/port
export YALP_HOST="0.0.0.0"
export YALP_PORT="8000"

# Start the server
yalp
```

### Quick request example

Once the proxy is running you can forward a request with `curl` (or any HTTP
client).  For instance, to proxy a chat completion request to an OpenAI‑style
endpoint:

```bash
curl -X POST "http://$YALP_HOST:$YALP_PORT/v1/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
```

The proxy will forward the request to `YALP_BASE/v1/chat/completions`, apply the
`ReasoningRenamer` transformation (if applicable), and stream the response
back to `curl`.

You can also run it directly with Python:

```bash
python -m yalp
```

The server will be reachable at `http://<YALP_HOST>:<YALP_PORT>/` and will forward
all paths to the upstream service.

## Development

If you want to work on the codebase:

1. Clone the repository.
2. Install development dependencies (FastAPI, httpx, pytest, etc.) – they are
   already listed in `pyproject.toml`.
3. Run the proxy in a virtual environment as shown above.

Unit‑tests are not shipped yet, but you can add them under a `tests/` folder and
run them with `pytest`.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes, ensuring they keep the same minimal style as the existing
   code.
4. Open a pull request describing the change.

## License

This project is licensed under the **Apache License, Version 2.0**. See the
official license text at https://www.apache.org/licenses/LICENSE-2.0 for
full details.
