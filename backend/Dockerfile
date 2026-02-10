FROM python:3.11-slim

WORKDIR /app

# Install system deps if needed (e.g. for obstore / libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Required when using STORAGE_BACKEND=minio
RUN pip install --no-cache-dir obstore

COPY . .

# Create uploads dir for local storage; alembic/versions is not copied (.dockerignore)
RUN mkdir -p data/uploads alembic/versions

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
