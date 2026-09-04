import uuid
from pathlib import Path
from typing import Optional
import psycopg2
import psycopg2.extras
from fastapi import Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.paths import APP_DIR, UPLOADS_DIR
from app.upload_core import save_upload_file
from app.auth import verify_admin
from app.db import get_db_connection
from app.views import templates
from fastapi import APIRouter

router = APIRouter()
project_root = APP_DIR

@router.get("/admin/categories", response_class=HTMLResponse)
async def admin_categories(request: Request, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT
            id,
            title,
            slug,
            parent_slug,
            category_group,
            short_description,
            image_url,
            display_order,
            is_active
        FROM project_categories
        ORDER BY
            CASE WHEN parent_slug IS NULL THEN 0 ELSE 1 END,
            parent_slug,
            display_order,
            id;
    """)

    categories = cursor.fetchall()
    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_categories.html",
        context={
            "title": "Направления",
            "categories": categories
        }
    )


@router.get("/admin/categories/{category_id}/edit", response_class=HTMLResponse)
async def admin_category_edit(request: Request, category_id: int, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT
            id,
            title,
            slug,
            parent_slug,
            category_group,
            short_description,
            image_url,
            display_order,
            is_active
        FROM project_categories
        WHERE id = %s
        LIMIT 1;
    """, (category_id,))

    category = cursor.fetchone()

    certificate_model = None

    if category and category["slug"] == "tattoo-gift-certificate":
        cursor.execute("""
            SELECT
                id,
                title,
                alt_text,
                file_path,
                poster_path,
                original_filename,
                mime_type,
                file_size,
                updated_at
            FROM media_files
            WHERE (
                (
                    owner_type = 'category'
                    AND owner_id = %s
                )
                OR target_key = 'tattoo-gift-certificate'
              )
              AND block_key = 'certificate_3d'
              AND media_type = 'model'
            ORDER BY id DESC
            LIMIT 1;
        """, (category_id,))

        certificate_model = cursor.fetchone()

    cursor.close()
    connection.close()

    if not category:
        raise HTTPException(status_code=404, detail="Направление не найдено")

    return templates.TemplateResponse(
        request=request,
        name="admin_category_edit.html",
        context={
            "title": "Редактировать направление",
            "category": category,
            "certificate_model": certificate_model
        }
    )


@router.post("/admin/categories/{category_id}/edit")
async def admin_category_update(
    category_id: int,
    admin: str = Depends(verify_admin),
    title: str = Form(...),
    slug: str = Form(...),
    parent_slug: str = Form(""),
    category_group: str = Form("main"),
    short_description: str = Form(""),
    external_image_url: str = Form(""),
    image_file: Optional[UploadFile] = File(None),
    certificate_model_file: Optional[UploadFile] = File(None),
    certificate_poster_file: Optional[UploadFile] = File(None),
    display_order: int = Form(100),
    is_active: str = Form(None),
):
    active = is_active == "yes"
    uploaded_image_url = await save_upload_file(image_file)
    final_image_url = uploaded_image_url or external_image_url
    parent_value = parent_slug if parent_slug else None

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE project_categories
        SET
            title = %s,
            slug = %s,
            parent_slug = %s,
            category_group = %s,
            short_description = %s,
            image_url = %s,
            display_order = %s,
            is_active = %s
        WHERE id = %s;
    """, (
        title,
        slug,
        parent_value,
        category_group,
        short_description,
        final_image_url,
        display_order,
        active,
        category_id
    ))

    # ATS_CERTIFICATE_3D_BACKEND_V1
    if slug.strip() == "tattoo-gift-certificate":
        from pathlib import Path
        import uuid

        model_dir = UPLOADS_DIR / "media" / "models"
        poster_dir = UPLOADS_DIR / "media" / "posters"

        model_dir.mkdir(parents=True, exist_ok=True)
        poster_dir.mkdir(parents=True, exist_ok=True)

        async def save_certificate_file(
            upload,
            destination,
            allowed_extensions,
        ):
            if not upload or not upload.filename:
                return None, None, None, None

            extension = Path(upload.filename).suffix.lower()

            if extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Недопустимый формат файла: "
                        f"{extension or 'без расширения'}"
                    ),
                )

            generated_name = (
                uuid.uuid4().hex
                + extension
            )

            absolute_path = destination / generated_name

            total_size = 0

            try:
                with absolute_path.open("wb") as output:
                    while True:
                        chunk = await upload.read(1024 * 1024)

                        if not chunk:
                            break

                        total_size += len(chunk)
                        output.write(chunk)

            except Exception:
                absolute_path.unlink(missing_ok=True)
                raise

            relative_path = (
                "/"
                + str(
                    absolute_path.relative_to(project_root)
                ).replace("\\\\", "/")
            )

            return (
                relative_path,
                upload.filename,
                upload.content_type,
                total_size,
            )

        cursor.execute("""
            SELECT
                id,
                file_path,
                poster_path
            FROM media_files
            WHERE (
                (
                    owner_type = 'category'
                    AND owner_id = %s
                )
                OR target_key = 'tattoo-gift-certificate'
              )
              AND block_key = 'certificate_3d'
              AND media_type = 'model'
            ORDER BY id DESC
            LIMIT 1;
        """, (category_id,))

        existing_model = cursor.fetchone()

        new_model = None
        new_poster = None

        if (
            certificate_model_file
            and certificate_model_file.filename
        ):
            new_model = await save_certificate_file(
                certificate_model_file,
                model_dir,
                {".glb", ".gltf"},
            )

        if (
            certificate_poster_file
            and certificate_poster_file.filename
        ):
            new_poster = await save_certificate_file(
                certificate_poster_file,
                poster_dir,
                {".jpg", ".jpeg", ".png", ".webp"},
            )

        if new_model:
            (
                model_path,
                original_filename,
                mime_type,
                file_size,
            ) = new_model

            poster_path = (
                new_poster[0]
                if new_poster
                else (
                    existing_model[2]
                    if existing_model
                    else None
                )
            )

            if existing_model:
                cursor.execute("""
                    UPDATE media_files
                    SET
                        -- ATS_CERTIFICATE_CANONICAL_OWNER_V2
                        owner_type = 'category',
                        owner_id = %s,
                        block_key = 'certificate_3d',
                        media_type = 'model',
                        title = %s,
                        alt_text = %s,
                        file_path = %s,
                        poster_path = %s,
                        original_filename = %s,
                        mime_type = %s,
                        file_size = %s,
                        target_key = %s,
                        is_active = TRUE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                """, (
                    category_id,
                    "3D-модель подарочного сертификата",
                    (
                        "Интерактивная 3D-модель "
                        "подарочного сертификата "
                        "ArtToSlipAway"
                    ),
                    model_path,
                    poster_path,
                    original_filename,
                    mime_type,
                    file_size,
                    "tattoo-gift-certificate",
                    existing_model[0],
                ))
            else:
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
                        target_key
                    )
                    VALUES (
                        'category',
                        %s,
                        'certificate_3d',
                        'model',
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        10,
                        TRUE,
                        'tattoo-gift-certificate'
                    );
                """, (
                    category_id,
                    "3D-модель подарочного сертификата",
                    (
                        "Интерактивная 3D-модель "
                        "подарочного сертификата "
                        "ArtToSlipAway"
                    ),
                    model_path,
                    poster_path,
                    original_filename,
                    mime_type,
                    file_size,
                ))

            if existing_model:
                old_model_path = existing_model[1]

                if (
                    old_model_path
                    and old_model_path != model_path
                    and old_model_path.startswith("/uploads/")
                ):
                    (
                        project_root
                        / old_model_path.lstrip("/")
                    ).unlink(missing_ok=True)

                if new_poster:
                    old_poster_path = existing_model[2]

                    if (
                        old_poster_path
                        and old_poster_path != poster_path
                        and old_poster_path.startswith("/uploads/")
                    ):
                        (
                            project_root
                            / old_poster_path.lstrip("/")
                        ).unlink(missing_ok=True)

        elif new_poster and existing_model:
            poster_path = new_poster[0]

            cursor.execute("""
                UPDATE media_files
                SET
                    owner_type = 'category',
                    owner_id = %s,
                    block_key = 'certificate_3d',
                    media_type = 'model',
                    poster_path = %s,
                    target_key = %s,
                    is_active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """, (
                category_id,
                poster_path,
                "tattoo-gift-certificate",
                existing_model[0],
            ))

            old_poster_path = existing_model[2]

            if (
                old_poster_path
                and old_poster_path != poster_path
                and old_poster_path.startswith("/uploads/")
            ):
                (
                    project_root
                    / old_poster_path.lstrip("/")
                ).unlink(missing_ok=True)

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(url="/admin/categories", status_code=303)
