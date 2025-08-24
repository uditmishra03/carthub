# Use Python 3.12 slim image for database migrations
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy migration scripts and schema
COPY . .

# Create non-root user
RUN groupadd -r dbuser && useradd -r -g dbuser dbuser
RUN chown -R dbuser:dbuser /app
USER dbuser

# Default command runs migrations
CMD ["python", "migrate.py"]
