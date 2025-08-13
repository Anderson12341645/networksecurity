# Dockerfile
FROM python:3.11-slim-bookworm

# Install OpenSSL and create cert directory
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssl && \
    mkdir -p /app/certs

WORKDIR /app
COPY . /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        libssl-dev \
        awscli && \
    update-ca-certificates --fresh && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade certifi

CMD ["python3", "app.py"]