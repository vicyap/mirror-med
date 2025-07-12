FROM ghcr.io/astral-sh/uv:python3.13-bookworm AS builder
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential python3-dev && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY src ./src

# Install the project
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm
WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copy application from builder stage
COPY --from=builder /app /app

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

CMD ["mirror-med-api"]
