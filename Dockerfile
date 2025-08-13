# Use a newer base image with updated repositories
FROM python:3.11-slim-bookworm

WORKDIR /app
COPY . /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        openssl \
        libssl-dev \
        awscli && \
    update-ca-certificates --fresh && \
    rm -rf /var/lib/apt/lists/*
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /app/private.key \
    -out /app/certificate.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade certifi

CMD ["python3", "app.py"]


