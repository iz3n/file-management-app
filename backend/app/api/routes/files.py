import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, Depends, File, Path, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.file import FileMetadataResponse, ListFilesResponse, UploadResponse
from app.services.file_service import upload_csv, read_csv
from app.services.metadata_service import list_files, get_file_metadata_service

router = APIRouter()

# Bounds for pagination (avoid huge queries and storage ValueError)
PAGE_MIN = 1
PAGE_SIZE_MIN = 1
PAGE_SIZE_MAX = 100


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await asyncio.to_thread(upload_csv, file, db)


@router.get("/", response_model=ListFilesResponse)
def get_files(
    db: Session = Depends(get_db),
    page: int = Query(PAGE_MIN, ge=PAGE_MIN, description="Page number"),
    page_size: int = Query(10, ge=PAGE_SIZE_MIN, le=PAGE_SIZE_MAX, description="Items per page"),
    filename_contains: Optional[str] = Query(None, description="Filter by filename (substring, case-insensitive)"),
    uploaded_after: Optional[datetime] = Query(None, description="Filter files uploaded after this datetime"),
    uploaded_before: Optional[datetime] = Query(None, description="Filter files uploaded before this datetime"),
):
    return list_files(
        db,
        page=page,
        page_size=page_size,
        filename_contains=filename_contains,
        uploaded_after=uploaded_after,
        uploaded_before=uploaded_before,
    )


@router.get("/{file_id}/metadata", response_model=FileMetadataResponse)
async def get_file_metadata(
    db: Session = Depends(get_db),
    file_id: int = Path(..., ge=1),
):
    return get_file_metadata_service(db, file_id=file_id)


@router.get("/{file_id}/data")
async def read_file(
    file_id: int = Path(..., ge=1),
    page: int = Query(PAGE_MIN, ge=PAGE_MIN, description="Page number"),
    page_size: int = Query(10, ge=PAGE_SIZE_MIN, le=PAGE_SIZE_MAX, description="Rows per page"),
    db: Session = Depends(get_db),
):
    file = get_file_metadata_service(db, file_id=file_id)
    try:
        content = await read_csv(file.filename, page=page, page_size=page_size)
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File data not found on storage")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
