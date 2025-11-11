# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# No local database directory needed; using MongoDB

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/backend

# Expose port
EXPOSE 5000

# Change to backend directory and run the application via Gunicorn for production
WORKDIR /app/backend

# Environment variable allowing override of workers etc.
ENV GUNICORN_WORKERS=3
ENV GUNICORN_THREADS=2
ENV GUNICORN_TIMEOUT=90

# Default command (can be overridden) using gunicorn
CMD ["gunicorn", "-c", "../gunicorn.conf.py", "wsgi:app"]