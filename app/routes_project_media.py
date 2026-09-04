from typing import Optional

import psycopg2.extras
from fastapi import Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse

from app.media_core import (
    detect_media_type,
    save_media_file,
    save_poster_file,
    public_media_path_to_file,
)


def register_project_media_routes(app, get_db_connection, verify_admin):
    @app.get("/api/project-media/{slug}")
    async def api_project_media(slug: str):
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
            WHERE slug = %s
            LIMIT 1;
        """, (slug,))

        project = cursor.fetchone()

        if not project:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Проект не найден")

        owner_type = resolve_project_media_owner(project["project_type"])

        cursor.execute("""
            SELECT
                id,
                owner_type,
                owner_id,
                block_key,
                media_type,
                title,
                alt_text,
                file_path,
                poster_path,
                original_filename,
                sort_order,
                is_active,
                created_at
            FROM media_files
            WHERE is_active = TRUE
              AND owner_id = %s
              AND owner_type = %s
            ORDER BY
                sort_order ASC,
                created_at ASC,
                id ASC;
        """, (project["id"], owner_type))

        media = cursor.fetchall()

        cursor.close()
        connection.close()

        return {
            "project": {
                "id": project["id"],
                "title": project["title"],
                "slug": project["slug"],
                "project_type": project["project_type"],
                "status": project["status"]
            },
            "media": media
        }

    # === /project media api ===


    # === project covers api ===

    @app.get("/api/project-covers")
    async def api_project_covers():
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT DISTINCT ON (p.slug)
                p.id AS project_id,
                p.slug,
                p.title AS project_title,
                p.project_type,
                p.status,

                mf.id AS media_id,
                mf.media_type,
                mf.title AS media_title,
                mf.alt_text,
                mf.file_path,
                mf.poster_path,
                mf.original_filename,
                mf.sort_order
            FROM projects p
            JOIN media_files mf
                ON mf.owner_id = p.id
               AND mf.owner_type = CASE
                   WHEN p.project_type IN ('free_sketch', 'sketch') THEN 'free_sketch'
                   WHEN p.project_type = 'portfolio' THEN 'portfolio'
                   ELSE 'project'
               END
               AND mf.is_active = TRUE
            WHERE p.status NOT IN ('hidden', 'draft')
            ORDER BY
                p.slug,
                mf.sort_order ASC,
                mf.created_at ASC,
                mf.id ASC;
        """)

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        result = {}

        for row in rows:
            display_path = row["file_path"]

            if row["media_type"] in ("video", "model") and row.get("poster_path"):
                display_path = row["poster_path"]

            result[row["slug"]] = {
                "project_id": row["project_id"],
                "project_title": row["project_title"],
                "project_type": row["project_type"],
                "media_id": row["media_id"],
                "media_type": row["media_type"],
                "media_title": row["media_title"],
                "alt_text": row["alt_text"],
                "file_path": row["file_path"],
                "poster_path": row["poster_path"],
                "display_path": display_path,
                "original_filename": row["original_filename"],
                "sort_order": row["sort_order"]
            }

        return result

    # === /project covers api ===


    # === inline project and carousel media admin ===

    PROJECT_MEDIA_OWNER_TYPES = {"project", "free_sketch", "portfolio"}
    PROJECT_MEDIA_BLOCKS = {
        "project_gallery",
        "portfolio_gallery",
        "free_sketch_gallery",
        "project_process",
        "project_3d"
    }

    CAROUSEL_BLOCK_KEY = "home_carousel"


    def resolve_project_media_owner(project_type: str, requested_owner_type: str = "auto") -> str:
        if requested_owner_type in PROJECT_MEDIA_OWNER_TYPES:
            return requested_owner_type

        if project_type in {"free_sketch", "sketch"}:
            return "free_sketch"

        if project_type in {"portfolio"}:
            return "portfolio"

        return "project"


    @app.get("/api/admin/projects/{project_id}/media")
    async def api_admin_project_media(
        project_id: int,
        admin: str = Depends(verify_admin)
    ):
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT id, title, slug, project_type, status
            FROM projects
            WHERE id = %s
            LIMIT 1;
        """, (project_id,))

        project = cursor.fetchone()

        if not project:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Проект не найден")

        owner_type = resolve_project_media_owner(project["project_type"])

        cursor.execute("""
            SELECT *
            FROM media_files
            WHERE owner_id = %s
              AND owner_type = %s
            ORDER BY sort_order ASC, created_at ASC, id ASC;
        """, (project_id, owner_type))

        media_files = cursor.fetchall()

        cursor.close()
        connection.close()

        return {
            "project": project,
            "media_files": media_files
        }


    @app.post("/admin/projects/{project_id}/media/upload")
    async def admin_project_media_upload(
        project_id: int,
        media_owner_type: str = Form("auto"),
        block_key: str = Form("project_gallery"),
        media_type: str = Form("auto"),
        title: str = Form(""),
        alt_text: str = Form(""),
        sort_order: int = Form(100),
        file: UploadFile = File(...),
        poster_file: UploadFile | None = File(None),
        admin: str = Depends(verify_admin)
    ):
        if block_key not in PROJECT_MEDIA_BLOCKS:
            raise HTTPException(status_code=400, detail="Недопустимый блок проекта")

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT id, project_type
            FROM projects
            WHERE id = %s
            LIMIT 1;
        """, (project_id,))

        project = cursor.fetchone()

        if not project:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Проект не найден")

        owner_type = resolve_project_media_owner(project["project_type"], media_owner_type)
        detected_type = detect_media_type(file.filename, media_type)

        saved_path, file_size = await save_media_file(file, detected_type)
        poster_path, _poster_size = await save_poster_file(poster_file)

        cursor.execute("""
            INSERT INTO media_files (
                owner_type,
                owner_id,
                block_key,
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
            VALUES (%s, %s, %s, %s, NULLIF(%s, ''), NULLIF(%s, ''), %s, NULLIF(%s, ''), %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP);
        """, (
            owner_type,
            project_id,
            block_key,
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
            url=f"/admin/projects/{project_id}/edit",
            status_code=status.HTTP_303_SEE_OTHER
        )


    @app.post("/admin/projects/{project_id}/media/{media_id}/edit")
    async def admin_project_media_edit(
        project_id: int,
        media_id: int,
        title: str = Form(""),
        alt_text: str = Form(""),
        block_key: str = Form("project_gallery"),
        sort_order: int = Form(100),
        admin: str = Depends(verify_admin)
    ):
        if block_key not in PROJECT_MEDIA_BLOCKS:
            raise HTTPException(status_code=400, detail="Недопустимый блок проекта")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE media_files
            SET title = NULLIF(%s, ''),
                alt_text = NULLIF(%s, ''),
                block_key = %s,
                sort_order = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND owner_id = %s
              AND owner_type = (
                  SELECT CASE
                      WHEN project_type IN ('free_sketch', 'sketch') THEN 'free_sketch'
                      WHEN project_type = 'portfolio' THEN 'portfolio'
                      ELSE 'project'
                  END
                  FROM projects
                  WHERE id = %s
              );
        """, (
            title.strip(),
            alt_text.strip(),
            block_key,
            sort_order,
            media_id,
            project_id,
            project_id
        ))

        connection.commit()
        cursor.close()
        connection.close()

        return RedirectResponse(
            url=f"/admin/projects/{project_id}/edit",
            status_code=status.HTTP_303_SEE_OTHER
        )


    @app.post("/admin/projects/{project_id}/media/{media_id}/toggle")
    async def admin_project_media_toggle(
        project_id: int,
        media_id: int,
        admin: str = Depends(verify_admin)
    ):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE media_files
            SET is_active = NOT is_active,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND owner_id = %s
              AND owner_type = (
                  SELECT CASE
                      WHEN project_type IN ('free_sketch', 'sketch') THEN 'free_sketch'
                      WHEN project_type = 'portfolio' THEN 'portfolio'
                      ELSE 'project'
                  END
                  FROM projects
                  WHERE id = %s
              );
        """, (media_id, project_id, project_id))

        connection.commit()
        cursor.close()
        connection.close()

        return RedirectResponse(
            url=f"/admin/projects/{project_id}/edit",
            status_code=status.HTTP_303_SEE_OTHER
        )


    @app.post("/admin/projects/{project_id}/media/{media_id}/delete")
    async def admin_project_media_delete(
        project_id: int,
        media_id: int,
        admin: str = Depends(verify_admin)
    ):
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT file_path, poster_path
            FROM media_files
            WHERE id = %s
              AND owner_id = %s
              AND owner_type = (
                  SELECT CASE
                      WHEN project_type IN ('free_sketch', 'sketch') THEN 'free_sketch'
                      WHEN project_type = 'portfolio' THEN 'portfolio'
                      ELSE 'project'
                  END
                  FROM projects
                  WHERE id = %s
              );
        """, (media_id, project_id, project_id))

        row = cursor.fetchone()

        if row:
            for key in ["file_path", "poster_path"]:
                absolute = public_media_path_to_file(row.get(key))
                if absolute and absolute.exists():
                    absolute.unlink()

            cursor.execute("""
                DELETE FROM media_files
                WHERE id = %s
                  AND owner_id = %s
                  AND owner_type = (
                  SELECT CASE
                      WHEN project_type IN ('free_sketch', 'sketch') THEN 'free_sketch'
                      WHEN project_type = 'portfolio' THEN 'portfolio'
                      ELSE 'project'
                  END
                  FROM projects
                  WHERE id = %s
              );
            """, (media_id, project_id, project_id))

            connection.commit()

        cursor.close()
        connection.close()

        return RedirectResponse(
            url=f"/admin/projects/{project_id}/edit",
            status_code=status.HTTP_303_SEE_OTHER
        )
