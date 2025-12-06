FROM python:3.11-slim

# Set build arguments
ARG ENVIRONMENT=development

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=${ENVIRONMENT}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/uploads /app/data/exports /app/data/logs && \
    chmod -R 755 /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
# Use --reload for development, remove for production
CMD if [ "$ENVIRONMENT" = "production" ]; then \
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4; \
    else \
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
    fi
