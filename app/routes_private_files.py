"""Client attachments are never served through the public static mount."""
import hashlib
import re

import psycopg2.extras
from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse

from app.paths import PRIVATE_UPLOADS_DIR


def private_file_response(row):
    if not row:
        raise HTTPException(status_code=404, detail="Файл не найден")
    key = str(row["file_path"])
    if not re.fullmatch(r"private/[a-f0-9]{32}\.(?:jpg|jpeg|png|webp|pdf)", key):
        # Legacy public references must be migrated, never followed automatically.
        raise HTTPException(status_code=404, detail="Файл недоступен")
    path = PRIVATE_UPLOADS_DIR / key.split("/", 1)[1]
    if not path.is_file() or path.is_symlink():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=row.get("original_filename") or path.name,
        content_disposition_type="attachment",
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer",
                 "X-Content-Type-Options": "nosniff", "X-Robots-Tag": "noindex, nofollow"},
    )


def register_private_file_routes(app, get_db_connection, verify_admin):
    def fetch_file(file_id, token=None):
        connection = get_db_connection()
        try:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                if token is None:
                    cursor.execute("SELECT * FROM lead_files WHERE id = %s", (file_id,))
                else:
                    if not 20 <= len(token) <= 128:
                        raise HTTPException(status_code=404, detail="Файл не найден")
                    cursor.execute("""
                        SELECT f.* FROM lead_files f
                        JOIN leads l ON l.id = f.lead_id
                        JOIN client_access_tokens t ON t.lead_id = l.id
                        WHERE f.id = %s AND t.token_hash = %s AND t.is_active = TRUE
                          AND (t.expires_at IS NULL OR t.expires_at > NOW())
                          AND l.trashed_at IS NULL
                        LIMIT 1
                    """, (file_id, hashlib.sha256(token.encode()).hexdigest()))
                return cursor.fetchone()
        finally:
            connection.close()

    @app.get("/admin/lead-files/{file_id}")
    def admin_attachment(file_id: int, admin: str = Depends(verify_admin)):
        return private_file_response(fetch_file(file_id))

    @app.get("/client/{token}/files/{file_id}")
    def client_attachment(token: str, file_id: int):
        return private_file_response(fetch_file(file_id, token))
