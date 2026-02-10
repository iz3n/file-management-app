from sqlalchemy import Column, String, Integer, TIMESTAMP, func
from datetime import datetime
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class FileMetadata(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # file size in bytes
    rows: Mapped[int] = mapped_column(Integer)
    columns: Mapped[int] = mapped_column(Integer)
    uploaded_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
