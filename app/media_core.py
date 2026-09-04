from pathlib import Path
from typing import Optional
import uuid

from fastapi import HTTPException, UploadFile

from app.paths import MEDIA_ROOT

MEDIA_PUBLIC_PREFIX = "/uploads/media"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
MODEL_EXTENSIONS = {".glb", ".gltf", ".obj", ".stl", ".usdz"}

MAX_UPLOAD_SIZE = 500 * 1024 * 1024
UPLOAD_CHUNK_SIZE = 1024 * 1024


def ensure_media_dirs():
    for folder in ("images", "videos", "models", "posters"):
        (MEDIA_ROOT / folder).mkdir(parents=True, exist_ok=True)


def normalize_extension(filename: str) -> str:
    return Path(filename or "").suffix.lower()


def detect_media_type(filename: str, fallback: str = "") -> str:
    extension = normalize_extension(filename)

    if extension in IMAGE_EXTENSIONS:
        return "image"

    if extension in VIDEO_EXTENSIONS:
        return "video"

    if extension in MODEL_EXTENSIONS:
        return "model"

    if fallback in {"image", "video", "model"}:
        return fallback

    raise HTTPException(
        status_code=400,
        detail="Неподдерживаемый тип файла"
    )


def validate_media_extension(filename: str, media_type: str):
    extension = normalize_extension(filename)

    allowed = {
        "image": IMAGE_EXTENSIONS,
        "video": VIDEO_EXTENSIONS,
        "model": MODEL_EXTENSIONS,
        "poster": IMAGE_EXTENSIONS,
    }.get(media_type)

    if not allowed or extension not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Недопустимое расширение файла"
        )

    return extension


async def _write_upload(file: UploadFile, destination: Path, error_detail: str) -> int:
    total_size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                total_size += len(chunk)

                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=400, detail=error_detail)

                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    return total_size


async def save_media_file(file: UploadFile, media_type: str):
    ensure_media_dirs()

    extension = validate_media_extension(file.filename, media_type)

    folder_map = {
        "image": "images",
        "video": "videos",
        "model": "models",
    }

    folder = folder_map.get(media_type)

    if not folder:
        raise HTTPException(
            status_code=400,
            detail="Недопустимый тип медиа"
        )

    filename = f"{uuid.uuid4().hex}{extension}"
    destination = MEDIA_ROOT / folder / filename
    file_size = await _write_upload(file, destination, "Файл слишком большой")

    public_path = f"{MEDIA_PUBLIC_PREFIX}/{folder}/{filename}"

    return public_path, file_size


async def save_poster_file(file: Optional[UploadFile]):
    if not file or not file.filename:
        return "", 0

    ensure_media_dirs()

    extension = validate_media_extension(file.filename, "poster")

    filename = f"{uuid.uuid4().hex}{extension}"
    destination = MEDIA_ROOT / "posters" / filename
    file_size = await _write_upload(
        file,
        destination,
        "Файл постера слишком большой",
    )

    public_path = f"{MEDIA_PUBLIC_PREFIX}/posters/{filename}"

    return public_path, file_size


def public_media_path_to_file(public_path: str):
    if not public_path:
        return None

    if not public_path.startswith(MEDIA_PUBLIC_PREFIX + "/"):
        return None

    relative = public_path.replace(MEDIA_PUBLIC_PREFIX + "/", "", 1)
    absolute = (MEDIA_ROOT / relative).resolve()

    try:
        absolute.relative_to(MEDIA_ROOT.resolve())
    except ValueError:
        return None

    return absolute
