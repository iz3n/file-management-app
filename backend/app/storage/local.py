import csv
import os
from uuid import uuid4

import obstore as obs
from fastapi import HTTPException
from app.core.config import get_settings
from app.helpers.minio_check import minio_check
from app.storage.base import Storage

_settings = get_settings()


def _empty_page(page: int, page_size: int) -> dict:
    return {
        "data": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": 0,
    }

def _parse_csv_and_paginate(content: bytes, page: int, page_size: int) -> dict:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("File must be UTF-8 encoded")

    sample = text[:4096] if len(text) > 4096 else text
    if not sample.strip():
        return _empty_page(page, page_size)

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(text.splitlines(), dialect=dialect)
    rows = list(reader)

    if not rows or len(rows) < 2:
        return _empty_page(page, page_size)

    headers = rows[0]
    data = []
    for row in rows[1:]:
        if len(row) != len(headers):
            continue
        data.append(dict(zip(headers, row)))

    total = len(data)
    total_pages = (total + page_size - 1) // page_size
    start = min((page - 1) * page_size, total)

    return {
        "data": data[start : start + page_size],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


class LocalStorage(Storage):

    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        # MinIO store created on first use so minio_check() errors happen during a request → proper HTTP response
        self._minio_store = None

    def _get_minio_store(self):
        """Lazy MinIO connection so minio_check() runs during a request and HTTPException is returned to client."""
        if self._minio_store is None:
            self._minio_store = minio_check()
        return self._minio_store

    def save(self, content: bytes, filename: str) -> str:
        if _settings.STORAGE_BACKEND == "minio":
            _, ext = os.path.splitext(filename)
            unique_name = f"{uuid4()}{ext}" if ext else str(uuid4())
            obs.put(self._get_minio_store(), unique_name, content)
            return unique_name

        _, ext = os.path.splitext(filename)
        unique_name = f"{uuid4()}{ext}" if ext else str(uuid4())
        path = os.path.join(self.base_path, unique_name)
        with open(path, "wb") as f:
            f.write(content)
        return unique_name

    def read(
        self,
        unique_name: str,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        if page < 1:
            page = 1
        if page_size <= 0:
            raise ValueError("page_size must be greater than 0")
        if _settings.STORAGE_BACKEND == "minio":
            try:
                result = obs.get(self._get_minio_store(), unique_name)
                content = bytes(result.bytes())
            except Exception as e:
                msg = str(e)
                error_message = "".join(x for x in ("Connection", "Timeout", "ConnectionRefused", "Connection reset", "NoSuchBucket") if x in msg)
                if error_message:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Storage unavailable: {error_message}",
                    )
                if "NoSuchKey" in msg:
                    raise HTTPException(status_code=404, detail=f"File {unique_name} not found")
                raise HTTPException(status_code=502, detail=f"Storage error: {e}")
            return _parse_csv_and_paginate(content, page, page_size)

        path = os.path.join(self.base_path, unique_name)
        if not os.path.isfile(path):
            path = os.path.join(self.base_path, unique_name + ".csv")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File {unique_name} not found")

        with open(path, "rb") as f:
            content = f.read()
        return _parse_csv_and_paginate(content, page, page_size)