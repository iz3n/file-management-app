# Running with Docker Compose

## Requirements

- **Use Docker Compose V2** (command: `docker compose` with a space).  
  The old `docker-compose` (v1) can hit a `KeyError: 'ContainerConfig'` when recreating containers with newer Docker Engine. If you see that error, use:

  ```bash
  docker compose up --build
  ```

  If you only have v1 installed, install the Compose V2 plugin or run:  
  `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock docker/compose:latest up --build` from the project root.

## Quick start

From the project root (datavisyn/):

```bash
docker compose up --build
```

- **Frontend:** http://localhost:3000  
- **Backend API:** http://localhost:8000  
- **PostgreSQL:** localhost:5433 (user/pass/db: `datavisyn`)

---

## Storage type (important)

The backend can store uploaded CSV files in two ways. **You must choose one** via the `STORAGE_BACKEND` variable in docker-compose.yml.

### 1. Local filesystem (default)

- **`STORAGE_BACKEND=local`** (default in `docker-compose.yml`)
- Files are stored in the backend container under `/app/data/uploads`, persisted in the `backend_uploads` volume.

### 2. MinIO (S3-compatible object store)

- Set **`STORAGE_BACKEND=minio`** in the `backend` service in `docker-compose.yml`.
- Ensure MinIO env vars in the backend match the MinIO service:
  - `MINIO_ENDPOINT=minio:9000`
  - `MINIO_ACCESS_KEY=minioadmin`
  - `MINIO_SECRET_KEY=minioadmin`
  - `MINIO_BUCKET=uploads`
- Create the bucket `uploads` in the MinIO console (http://localhost:9001) if it does not exist.

**Summary:** To switch from local to MinIO, change `STORAGE_BACKEND` to `minio` and run with the `minio` profile. To switch back, set `STORAGE_BACKEND=local` and you can omit the `minio` profile.
