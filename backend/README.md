# Backend

FastAPI backend for the file management app. Handles CSV uploads, metadata storage in PostgreSQL, and file storage on local disk or MinIO (S3-compatible).

## Features

- **File upload**: CSV-only uploads with size limit and UTF-8 validation
- **File list**: Paginated list with filters (filename substring, date range)
- **File metadata**: Get rows/columns/size and upload time by file ID
- **File data**: Paginated CSV data by file ID
- **Storage backends**: Local filesystem or MinIO (S3-compatible)
- **Database**: PostgreSQL with SQLAlchemy and Alembic migrations

## Requirements

- **Python 3.11+**
- **PostgreSQL** (for metadata and app runtime; tests use SQLite)
- **Python dependencies**: see `requirements.txt` (FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, obstore, psycopg2-binary, etc.).
- **MinIO server** (optional): only when `STORAGE_BACKEND=minio`; ensure the bucket exists or the app can create it at startup

## Project structure

```
backend/
├── app/
│   ├── api/routes/   # FastAPI route handlers (files)
│   ├── core/         # Config (Pydantic Settings)
│   ├── db/           # SQLAlchemy base, models
│   ├── helpers/      # MinIO connection and bucket setup
│   ├── schemas/      # Pydantic request/response models
│   ├── services/     # Business logic (file, metadata)
│   ├── storage/      # Storage abstraction (local + MinIO)
│   └── main.py       # FastAPI app, CORS, static files
├── alembic/          # Database migrations
├── tests/            # Pytest tests
├── requirements.txt
├── Dockerfile
└── entrypoint.sh     # Migrations + uvicorn (Just for docker compose)
```

## Setup (local development)

1. **Create a virtual environment and install dependencies**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment variables**

   Create a `.env` file in `backend/` (or export variables). All of the following are required by the app config:

   | Variable | Description | Example |
   |----------|--------------|---------|
   | `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:pass@localhost:5432/datavisyn` |
   | `UPLOAD_DIR` | Directory for local uploads | `data/uploads` |
   | `MAX_UPLOAD_BYTES` | Max upload size (bytes) | `52428800` (50 MB) by default |
   | `STORAGE_BACKEND` | `local` or `minio` | `local` |
   | `MINIO_ENDPOINT` | MinIO URL (with scheme) | `http://localhost:9000` |
   | `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
   | `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |
   | `MINIO_BUCKET` | MinIO bucket name | `uploads` |
   | `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:5173,http://127.0.0.1:5173` |

   For **local storage only**, you can set `STORAGE_BACKEND=local` or `STORAGE_BACKEND=minio`; MinIO vars still need to be present if `STORAGE_BACKEND=local` but are unused.

3. **Database and migrations**

   Create the database, then run migrations:

   ```bash
   alembic revision --autogenerate -m "initial"
   alembic upgrade head
   ```

4. **Run the server**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   - API: http://localhost:8000  
   - OpenAPI docs: http://localhost:8000/docs  

## API overview

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/files/upload` | Upload a CSV file |
| `GET` | `/files/` | List files (paginated, optional filters) |
| `GET` | `/files/{file_id}/metadata` | Get file metadata by ID |
| `GET` | `/files/{file_id}/data` | Get paginated CSV data by file ID |

**Query parameters**

- **List files**: `page`, `page_size`, `filename_contains`, `uploaded_after`, `uploaded_before`
- **File data**: `page`, `page_size`

Responses use the schemas in `app/schemas/file.py`. Errors (e.g. invalid file, storage errors, missing bucket) return appropriate status codes and a `detail` message in the JSON body.

## Storage backends

- **`local`**: Files are stored under `UPLOAD_DIR` on disk. The app creates the directory if needed.
- **`minio`**: Files are stored in the configured MinIO bucket. Use a full URL for `MINIO_ENDPOINT` (e.g. `http://minio:9000` or `http://localhost:9000`). create the bucket in the MinIO Console (e.g. http://localhost:9001).

## Tests

From the `backend/` directory with the virtual environment activated:

```bash
pytest tests/test_files_flow.py -v
```

Tests use an in-memory SQLite database and a temporary upload directory (see `tests/conftest.py`).

## Docker

See the project root `README.docker.md` and `docker-compose.yml` for running the backend with PostgreSQL and optional MinIO. The backend Dockerfile runs Alembic migrations (autogenerate in container if no migrations exist, then `upgrade head`) and then starts uvicorn.

### CSV assumptions

- CSV files must be UTF-8 encoded text
- The first row is treated as the header
- Default delimiter is `,`
- Large files (tens of thousands of rows) are supported via pagination

## Error handling

- Validation errors (invalid file type, size, encoding) return `400`
- Missing files or buckets return `404`
- Storage/authentication issues (e.g. MinIO credentials) return `401` or `500`
- All errors return a JSON body with a `detail` message




