# Use the official Python 3.10 runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

# Set working directory
WORKDIR /app

# Install system dependencies for Python package compilation
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' --shell /bin/bash user && \
    chown -R user:user /app
USER user

# Expose port (Railway will override this with $PORT)
EXPOSE 8080

# Health check - disabled for Railway (Railway has its own health monitoring)
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:${PORT:-8080}/ || exit 1

# Run with Gunicorn (production WSGI server)
# Note: Railway prioritizes Procfile over Dockerfile CMD
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} wsgi:app --workers 2 --timeout 120 --access-logfile - --error-logfile -"]