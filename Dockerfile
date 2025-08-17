# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Copy the application into the container.
COPY . /app

# Set working directory
WORKDIR /app

RUN uv sync --frozen --no-cache

# Expose port
EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
