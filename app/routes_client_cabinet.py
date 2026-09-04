import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import psycopg2.extras
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from app.config import site_base_url


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _public_file_path(path: str) -> str:
    path = str(path or "").strip()
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return path


def register_client_cabinet_routes(app, templates, get_db_connection, verify_admin):
    @app.get("/client/{token}", response_class=HTMLResponse)
    async def client_cabinet(request: Request, token: str):
        token = (token or "").strip()

        if len(token) < 20:
            raise HTTPException(status_code=404, detail="Кабинет не найден")

        token_hash = _hash_token(token)

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cursor.execute("""
                SELECT
                    t.id AS token_id,
                    t.created_at AS token_created_at,
                    t.expires_at AS token_expires_at,
                    l.*
                FROM client_access_tokens t
                JOIN leads l ON l.id = t.lead_id
                WHERE t.token_hash = %s
                  AND t.is_active = TRUE
                  AND (t.expires_at IS NULL OR t.expires_at > NOW())
                  AND l.trashed_at IS NULL
                LIMIT 1;
            """, (token_hash,))

            lead = cursor.fetchone()

            if not lead:
                raise HTTPException(status_code=404, detail="Кабинет не найден или ссылка устарела")

            cursor.execute("""
                UPDATE client_access_tokens
                SET last_opened_at = NOW()
                WHERE id = %s;
            """, (lead["token_id"],))

            cursor.execute("""
                SELECT
                    id,
                    file_path,
                    original_filename,
                    file_type,
                    created_at
                FROM lead_files
                WHERE lead_id = %s
                ORDER BY id ASC;
            """, (lead["id"],))

            files = []
            for row in cursor.fetchall():
                item = dict(row)
                item["public_path"] = f"/client/{token}/files/{item['id']}"
                files.append(item)

            connection.commit()

            return templates.TemplateResponse(
                request=request,
                name="client_cabinet.html",
                context={
                    "lead": dict(lead),
                    "files": files,
                    "site_url": site_base_url(),
                },
                headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer",
                         "X-Robots-Tag": "noindex, nofollow"},
            )

        except HTTPException:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()


    @app.post("/admin/leads/{lead_id}/client-link", response_class=HTMLResponse)
    async def admin_create_client_link(
        request: Request,
        lead_id: int,
        admin: str = Depends(verify_admin),
    ):
        token = secrets.token_urlsafe(36)
        token_hash = _hash_token(token)
        token_hint = token[-8:]
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cursor.execute("""
                SELECT id, name, contact, project_title, created_at
                FROM leads
                WHERE id = %s
                  AND trashed_at IS NULL
                LIMIT 1;
            """, (lead_id,))

            lead = cursor.fetchone()

            if not lead:
                raise HTTPException(status_code=404, detail="Заявка не найдена")

            cursor.execute("""
                INSERT INTO client_access_tokens (
                    lead_id,
                    token_hash,
                    token_hint,
                    is_active,
                    expires_at
                )
                VALUES (%s, %s, %s, TRUE, %s)
                RETURNING id;
            """, (lead_id, token_hash, token_hint, expires_at))

            token_row = cursor.fetchone()
            connection.commit()

            client_url = f"{site_base_url()}/client/{token}"

            return templates.TemplateResponse(
                request=request,
                name="admin_client_link.html",
                context={
                    "lead": dict(lead),
                    "token_id": token_row["id"],
                    "client_url": client_url,
                    "expires_at": expires_at,
                },
            )

        except HTTPException:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()
