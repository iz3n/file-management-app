from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FileMetadataResponse(BaseModel):
    """Response schema for a single file's metadata (matches DB model)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    size: int | None
    rows: int
    columns: int
    uploaded_at: datetime


class ListFilesResponse(BaseModel):
    """Response schema for paginated file list."""
    data: list[FileMetadataResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UploadResponse(BaseModel):
    """Response schema after successful upload."""
    filename: str
    rows: int
    cols: int
    size: int
