FROM python:3.11-slim

ENV POETRY_VERSION=1.8.2 \
  POETRY_VIRTUALENVS_CREATE=false \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y curl git build-essential && \
  pip install "poetry==$POETRY_VERSION"

# Set working directory
WORKDIR /src

# Copy project files
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi

# Copy rest of the source code
COPY . .

# Default command — can be overridden
CMD ["poetry", "run", "python", "src/train.py"]