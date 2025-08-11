FROM python:3.11-slim-buster
WORKDIR /app
COPY . /app

# Update sources to use archive repositories
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian buster contrib main non-free" > /etc/apt/sources.list

RUN apt-get update && apt-get install -y awscli
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "app.py"]

