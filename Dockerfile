FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace

# Copy dependencies
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy app code
COPY ./app ./app

ENV PATH="/workspace/.venv/bin:$PATH"

# Expose the port
EXPOSE 8080

# Command to run the server
CMD ["python", "-m", "app.main"]