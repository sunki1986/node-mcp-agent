# Base image
FROM python:3.13-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# System deps (minimal)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (for Docker cache)
COPY pyproject.toml uv.lock ./

# Copy Chainlit config explicitly
COPY .chainlit/config.toml /app/frontend-chart-server/.chainlit/config.toml

# Create venv + install deps
RUN uv venv && uv sync --frozen

# Copy application code
COPY . .

# Chainlit default port
EXPOSE 7000

# Start Chainlit
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7000"]
