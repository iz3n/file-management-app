import asyncio
import csv
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import FileMetadata
from app.storage.local import LocalStorage
from app.helpers.minio_check import minio_check

_settings = get_settings()
_project_root = Path(__file__).resolve().parent.parent.parent
_storage = LocalStorage(str(_project_root / _settings.UPLOAD_DIR))

ALLOWED_EXTENSIONS = (".csv",)
MAX_UPLOAD_BYTES = _settings.MAX_UPLOAD_BYTES


def count_csv(content: bytes) -> tuple[int, int]:
    """Parse CSV and return (num_data_rows, num_columns)."""
    text = content.decode("utf-8")
    lines = text.splitlines()

    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(text)

    reader = csv.reader(lines, dialect)
    rows = list(reader)

    if not rows:
        return 0, 0

    num_rows = len(rows) - 1
    num_cols = len(rows[0])
    return num_rows, num_cols


def upload_csv(file: UploadFile, db: Session) -> dict:
    if not file.filename or not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = file.file.read()
    size = len(content)

    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB",
        )

    if size == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        rows, cols = count_csv(content)
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded text",
        )
    except csv.Error as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV format: {e}",
        )

    try:
        unique_name = _storage.save(content, file.filename)
    except Exception as e:
        msg = str(e)
        error_message = "".join(x for x in ("Connection", "Timeout", "ConnectionRefused", "Connection reset", "NoSuchBucket") if x in msg)
        if error_message:
            raise HTTPException(
                status_code=503,
                detail=f"Storage unavailable: {error_message}",
            )
        raise HTTPException(status_code=502, detail=f"Storage error: {e}")

    file_metadata = FileMetadata(
        filename=unique_name,
        size=size,
        rows=rows,
        columns=cols,
    )
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)

    return {
        "filename": unique_name,
        "rows": rows,
        "cols": cols,
        "size": size,
    }


async def read_csv(
    unique_name: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    if _settings.STORAGE_BACKEND == "minio":
        minio_check()
    return await asyncio.to_thread(_storage.read, unique_name, page, page_size)
