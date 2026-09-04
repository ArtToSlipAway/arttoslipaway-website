from typing import Optional

import psycopg2.extras
from fastapi import Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.media_core import (
    MEDIA_ROOT,
    MEDIA_PUBLIC_PREFIX,
    detect_media_type,
    save_media_file,
    save_poster_file,
    public_media_path_to_file,
)


def register_media_routes(app, templates, get_db_connection, verify_admin):
    @app.get("/admin/media", response_class=HTMLResponse)
    async def admin_media(request: Request, admin: str = Depends(verify_admin)):
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT
                id,
                title,
                slug,
                project_type,
                status
            FROM projects
            ORDER BY id DESC;
        """)

        projects = cursor.fetchall()

        cursor.execute("""
            SELECT *
            FROM media_files
            ORDER BY created_at DESC, id DESC;
        """)

        media_files = cursor.fetchall()

        cursor.close()
        connection.close()

        return templates.TemplateResponse(
            request=request,
            name="admin_media.html",
            context={
                "title": "Медиа-библиотека",
                "media_files": media_files,
                "projects": projects
            }
        )


    @app.post("/admin/media/upload")
    async def admin_media_upload(
        owner_type: str = Form("general"),
        owner_id: str = Form(""),
        block_key: str = Form(""),
        target_key: str = Form(""),
        media_type: str = Form("auto"),
        title: str = Form(""),
        alt_text: str = Form(""),
        sort_order: int = Form(100),
        file: UploadFile = File(...),
        poster_file: UploadFile | None = File(None),
        admin: str = Depends(verify_admin)
    ):
        if owner_type not in {"general", "visual", "project", "free_sketch", "portfolio"}:
            raise HTTPException(status_code=400, detail="Недопустимый тип блока")

        detected_type = detect_media_type(file.filename, media_type)

        saved_path, file_size = await save_media_file(file, detected_type)
        poster_result = await save_poster_file(poster_file)

        if isinstance(poster_result, tuple):
            poster_path = poster_result[0]
        else:
            poster_path = poster_result

        owner_id_value = None

        if owner_id.strip():
            try:
                owner_id_value = int(owner_id)
            except ValueError:
                owner_id_value = None

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO media_files (
                owner_type,
                owner_id,
                block_key,
                target_key,
                media_type,
                title,
                alt_text,
                file_path,
                poster_path,
                original_filename,
                mime_type,
                file_size,
                sort_order,
                is_active,
                updated_at
            )
            VALUES (%s, %s, NULLIF(%s, ''), NULLIF(%s, ''), %s, NULLIF(%s, ''), NULLIF(%s, ''), %s, NULLIF(%s, ''), %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP);
        """, (
            owner_type,
            owner_id_value,
            block_key.strip(),
            target_key.strip(),
            detected_type,
            title.strip(),
            alt_text.strip(),
            saved_path,
            poster_path or "",
            file.filename,
            file.content_type or "",
            file_size,
            sort_order
        ))

        connection.commit()
        cursor.close()
        connection.close()

        return RedirectResponse(
            url="/admin/media",
            status_code=status.HTTP_303_SEE_OTHER
        )



    @app.get("/admin/media/{media_id}/edit")
    async def admin_media_edit_page(
        request: Request,
        media_id: int,
        admin: str = Depends(verify_admin)
    ):
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT *
            FROM media_files
            WHERE id = %s;
        """, (media_id,))
        media_file = cursor.fetchone()

        if not media_file:
            cursor.close()
            connection.close()

            return RedirectResponse(
                url="/admin/media",
                status_code=status.HTTP_303_SEE_OTHER
            )

        cursor.execute("""
            SELECT id, title
            FROM projects
            ORDER BY id DESC;
        """)
        projects = cursor.fetchall()

        # ATS_MEDIA_CATEGORY_OWNER_V1
        cursor.execute("""
            SELECT
                id,
                title,
                slug
            FROM project_categories
            WHERE is_active = TRUE
            ORDER BY
                display_order ASC,
                id ASC;
        """)

        categories = cursor.fetchall()

        cursor.close()
        connection.close()

        return templates.TemplateResponse(
            request=request,
            name="admin_media_edit.html",
            context={
                "title": "Редактировать медиа",
                "media_file": media_file,
                "projects": projects,
                "categories": categories
            }
        )


    @app.post("/admin/media/{media_id}/edit")
    async def admin_media_edit(
        media_id: int,
        owner_type: str = Form("general"),
        owner_id: str = Form(""),
        block_key: str = Form(""),
        target_key: str = Form(""),
        media_type: str = Form("auto"),
        title: str = Form(""),
        alt_text: str = Form(""),
        sort_order: int = Form(100),
        is_active: str = Form(""),
        replacement_file: UploadFile | None = File(None),
        replacement_poster_file: UploadFile | None = File(None),
        admin: str = Depends(verify_admin)
    ):
        allowed_owner_types = {
            "general",
            "visual",
            "project",
            "free_sketch",
            "portfolio",
            "category",
        }

        if owner_type not in allowed_owner_types:
            raise HTTPException(
                status_code=400,
                detail="Недопустимый тип владельца медиа",
            )

        owner_id_value = None

        if owner_id.strip():
            try:
                owner_id_value = int(owner_id)
            except ValueError:
                owner_id_value = None

        active_value = bool(is_active)

        fields = [
            "owner_type = %s",
            "owner_id = %s",
            "block_key = NULLIF(%s, '')",
            "target_key = NULLIF(%s, '')",
            "title = NULLIF(%s, '')",
            "alt_text = NULLIF(%s, '')",
            "sort_order = %s",
            "is_active = %s"
        ]

        params = [
            owner_type,
            owner_id_value,
            block_key.strip(),
            target_key.strip(),
            title.strip(),
            alt_text.strip(),
            sort_order,
            active_value
        ]

        if replacement_file is not None and replacement_file.filename:
            detected_type = detect_media_type(replacement_file.filename, media_type)
            saved_path, file_size = await save_media_file(replacement_file, detected_type)

            fields.extend([
                "media_type = %s",
                "file_path = %s",
                "original_filename = %s",
                "mime_type = %s",
                "file_size = %s"
            ])

            params.extend([
                detected_type,
                saved_path,
                replacement_file.filename,
                replacement_file.content_type or "",
                file_size
            ])
        elif media_type in {"image", "video", "model"}:
            fields.append("media_type = %s")
            params.append(media_type)

        if replacement_poster_file is not None and replacement_poster_file.filename:
            poster_result = await save_poster_file(replacement_poster_file)

            if isinstance(poster_result, tuple):
                poster_path = poster_result[0]
            else:
                poster_path = poster_result

            fields.append("poster_path = NULLIF(%s, '')")
            params.append(poster_path or "")

        params.append(media_id)

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(f"""
            UPDATE media_files
            SET {", ".join(fields)},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, params)

        connection.commit()
        cursor.close()
        connection.close()

        return RedirectResponse(
            url="/admin/media",
            status_code=status.HTTP_303_SEE_OTHER
        )



    @app.post("/admin/media/{media_id}/delete")
    async def admin_media_delete(
        media_id: int,
        admin: str = Depends(verify_admin)
    ):
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT file_path, poster_path
            FROM media_files
            WHERE id = %s;
        """, (media_id,))

        row = cursor.fetchone()

        if row:
            for key in ["file_path", "poster_path"]:
                absolute = public_media_path_to_file(row.get(key))

                if absolute and absolute.exists():
                    absolute.unlink()

            cursor.execute("DELETE FROM media_files WHERE id = %s;", (media_id,))
            connection.commit()

        cursor.close()
        connection.close()

        return RedirectResponse(
            url="/admin/media",
            status_code=status.HTTP_303_SEE_OTHER
        )


    @app.post("/admin/media/{media_id}/toggle")
    async def admin_media_toggle(
        media_id: int,
        admin: str = Depends(verify_admin)
    ):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE media_files
            SET is_active = NOT is_active,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (media_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return RedirectResponse(
            url="/admin/media",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # === /admin media manager ===


    # === /admin cms hub ===
