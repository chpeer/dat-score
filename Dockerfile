# Stage 1: Build dependencies and install Python packages
FROM python:3.13.5-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && pip install poetry

# Copy only dependency files first for better caching
COPY pyproject.toml ./

# Install dependencies (no virtualenv)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the code (for building wheels if needed)
COPY . .

# Stage 2: Runtime image
FROM python:3.13.5-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app source code (excluding files in .dockerignore)
COPY . .

EXPOSE 8080

ENV FLASK_APP=main.py
ENV FLASK_ENV=production

CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "main:app"]
