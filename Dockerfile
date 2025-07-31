# ── Build Stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Don’t create venvs inside Poetry, write .pyc, or buffer stdout
ENV POETRY_VIRTUALENVS_CREATE=false \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# Install build tools & Poetry
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl build-essential git \
  && curl -sSL https://install.python-poetry.org | python3 - \
  && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Copy project metadata & install deps only
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --without dev --no-root

# ── Final Stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim

# keep same runtime envs
ENV POETRY_VIRTUALENVS_CREATE=false \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONPATH=/app/src


WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local         /usr/local
COPY --from=builder /root/.local       /root/.local


ENV PATH="/root/.local/bin:${PATH}"

#
# Copy your entire project (so that `src/` and `app/` land under `/app`)
COPY . .

# Expose Streamlit’s default port
EXPOSE 8501

# Launch from the repo root, pointing to the Streamlit entrypoint under src/app
CMD ["streamlit", "run", "src/app/main.py", "--server.port=8501", "--server.enableCORS=false"]