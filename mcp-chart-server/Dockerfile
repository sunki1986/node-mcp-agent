FROM python:3.13-slim

WORKDIR /app
COPY . /app/

RUN pip install --no-cache-dir uv

# Create venv
RUN uv venv

# Install dependencies into venv
RUN uv sync

EXPOSE 9000

# Use venv python directly
CMD ["/app/.venv/bin/python", "mcp_server.py"]
