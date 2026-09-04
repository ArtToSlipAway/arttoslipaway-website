from pathlib import Path
from typing import Collection, Optional
import uuid

from fastapi import HTTPException, UploadFile

from app.paths import PRIVATE_UPLOADS_DIR, UPLOADS_DIR

UPLOAD_DIR = UPLOADS_DIR
IMAGE_UPLOAD_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp"})
REFERENCE_UPLOAD_EXTENSIONS = frozenset({*IMAGE_UPLOAD_EXTENSIONS, ".pdf"})
MAX_UPLOAD_SIZE = 25 * 1024 * 1024
UPLOAD_CHUNK_SIZE = 1024 * 1024


async def save_upload_file(
    file: Optional[UploadFile],
    *,
    allowed_extensions: Collection[str] = IMAGE_UPLOAD_EXTENSIONS,
    private: bool = False,
) -> str:
    """Save a validated upload without loading the whole file into memory."""
    if not file or not file.filename:
        return ""

    extension = Path(file.filename).suffix.lower()
    allowed = {item.lower() for item in allowed_extensions}

    if extension not in allowed:
        readable = ", ".join(sorted(item.lstrip(".") for item in allowed))
        raise HTTPException(
            status_code=400,
            detail=f"Допустимые форматы: {readable}",
        )

    directory = PRIVATE_UPLOADS_DIR if private else UPLOAD_DIR
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}{extension}"
    destination = directory / safe_name
    total_size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                if total_size == 0 and not valid_file_header(chunk, extension):
                    raise HTTPException(status_code=400, detail="Содержимое файла не соответствует формату")
                total_size += len(chunk)

                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail="Файл слишком большой. Максимальный размер — 25 МБ",
                    )

                output.write(chunk)
            if total_size == 0:
                raise HTTPException(status_code=400, detail="Пустой файл")
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    return f"private/{safe_name}" if private else f"/uploads/{safe_name}"


def valid_file_header(data: bytes, extension: str) -> bool:
    """Basic format signature check, not an antivirus or full image decoder."""
    if extension in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff")
    if extension == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if extension == ".webp":
        return data.startswith(b"RIFF") and data[8:12] == b"WEBP"
    if extension == ".pdf":
        return data.startswith(b"%PDF-")
    return False
