# Multi-stage build for AgentTrace MCP server

# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install UV
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtualenv inside project dir and install production deps only
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src"

# Copy application code
COPY src/ /app/src/
COPY migrations/ /app/migrations/
COPY alembic.ini /app/

# Expose port
EXPOSE 8000

# Run the MCP server
CMD ["python", "-m", "mcp_tracer.server"]
