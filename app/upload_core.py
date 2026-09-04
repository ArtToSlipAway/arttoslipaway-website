from pathlib import Path
from typing import Collection, Optional
import uuid

from fastapi import HTTPException, UploadFile

from app.paths import UPLOADS_DIR

UPLOAD_DIR = UPLOADS_DIR
IMAGE_UPLOAD_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp"})
REFERENCE_UPLOAD_EXTENSIONS = frozenset({*IMAGE_UPLOAD_EXTENSIONS, ".pdf"})
MAX_UPLOAD_SIZE = 25 * 1024 * 1024
UPLOAD_CHUNK_SIZE = 1024 * 1024


async def save_upload_file(
    file: Optional[UploadFile],
    *,
    allowed_extensions: Collection[str] = IMAGE_UPLOAD_EXTENSIONS,
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

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}{extension}"
    destination = UPLOAD_DIR / safe_name
    total_size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                total_size += len(chunk)

                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail="Файл слишком большой. Максимальный размер — 25 МБ",
                    )

                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    return f"/uploads/{safe_name}"
