from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import FileMetadata


def list_files(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    filename_contains: Optional[str] = None,
    uploaded_after: Optional[datetime] = None,
    uploaded_before: Optional[datetime] = None,
):
    query = db.query(FileMetadata)
    if filename_contains is not None and filename_contains.strip():
        query = query.filter(FileMetadata.filename.ilike(f"%{filename_contains.strip()}%"))
    if uploaded_after is not None:
        query = query.filter(FileMetadata.uploaded_at >= uploaded_after)
    if uploaded_before is not None:
        query = query.filter(FileMetadata.uploaded_at <= uploaded_before)

    total = query.count()
    files = query.order_by(FileMetadata.uploaded_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return {"data": files, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}



def get_file_metadata_service(db: Session, file_id: int):
    file = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file