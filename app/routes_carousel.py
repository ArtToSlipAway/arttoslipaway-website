from typing import Optional
import psycopg2
import psycopg2.extras
from fastapi import Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.auth import verify_admin
from app.db import get_db_connection
from app.views import templates
from app.certificates import CERTIFICATE_SETTINGS_DEFAULTS, get_certificate_settings
from app.media_core import detect_media_type, save_media_file, save_poster_file, public_media_path_to_file
from fastapi import APIRouter

router = APIRouter()

CAROUSEL_BLOCK_KEY = "home_carousel"

@router.get("/admin/carousel", response_class=HTMLResponse)
async def admin_carousel(request: Request, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT *
        FROM media_files
        WHERE owner_type = 'visual'
          AND block_key = %s
        ORDER BY sort_order ASC, created_at ASC, id ASC;
    """, (CAROUSEL_BLOCK_KEY,))

    media_files = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM carousel_cards
        ORDER BY sort_order ASC, id ASC;
    """)

    carousel_cards = cursor.fetchall()

    # ATS_CAROUSEL_CERTIFICATE_SETTINGS_V1
    certificate_settings = (
        get_certificate_settings(
            connection
        )
    )

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_carousel.html",
        context={
            "title": "Карусель главной",
            "media_files": media_files,
            "carousel_cards": carousel_cards,
            "certificate_settings": certificate_settings
        }
    )


@router.post("/admin/carousel/media/upload")
async def admin_carousel_media_upload(
    media_type: str = Form("auto"),
    target_key: str = Form(""),
    title: str = Form(""),
    alt_text: str = Form(""),
    sort_order: int = Form(100),
    file: UploadFile = File(...),
    poster_file: UploadFile | None = File(None),
    admin: str = Depends(verify_admin)
):
    detected_type = detect_media_type(file.filename, media_type)

    saved_path, file_size = await save_media_file(file, detected_type)
    poster_path, _poster_size = await save_poster_file(poster_file)

    connection = get_db_connection()
    cursor = connection.cursor()

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
            target_key,
            is_active,
            updated_at
        )
        VALUES ('visual', NULL, %s, %s, NULLIF(%s, ''), NULLIF(%s, ''), %s, NULLIF(%s, ''), %s, %s, %s, %s, NULLIF(%s, ''), TRUE, CURRENT_TIMESTAMP);
    """, (
        CAROUSEL_BLOCK_KEY,
        detected_type,
        title.strip(),
        alt_text.strip(),
        saved_path,
        poster_path or "",
        file.filename,
        file.content_type or "",
        file_size,
        sort_order,
        target_key.strip()
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/carousel",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/carousel/media/{media_id}/edit")
async def admin_carousel_media_edit(
    media_id: int,
    target_key: str = Form(""),
    title: str = Form(""),
    alt_text: str = Form(""),
    sort_order: int = Form(100),
    admin: str = Depends(verify_admin)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE media_files
        SET title = NULLIF(%s, ''),
            alt_text = NULLIF(%s, ''),
            sort_order = %s,
            target_key = NULLIF(%s, ''),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
          AND owner_type = 'visual'
          AND block_key = %s;
    """, (
        title.strip(),
        alt_text.strip(),
        sort_order,
        target_key.strip(),
        media_id,
        CAROUSEL_BLOCK_KEY
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/carousel",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/carousel/media/{media_id}/toggle")
async def admin_carousel_media_toggle(
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
          AND owner_type = 'visual'
          AND block_key = %s;
    """, (media_id, CAROUSEL_BLOCK_KEY))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/carousel",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/carousel/media/{media_id}/delete")
async def admin_carousel_media_delete(
    media_id: int,
    admin: str = Depends(verify_admin)
):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT file_path, poster_path
        FROM media_files
        WHERE id = %s
          AND owner_type = 'visual'
          AND block_key = %s;
    """, (media_id, CAROUSEL_BLOCK_KEY))

    row = cursor.fetchone()

    if row:
        for key in ["file_path", "poster_path"]:
            absolute = public_media_path_to_file(row.get(key))
            if absolute and absolute.exists():
                absolute.unlink()

        cursor.execute("""
            DELETE FROM media_files
            WHERE id = %s
              AND owner_type = 'visual'
              AND block_key = %s;
        """, (media_id, CAROUSEL_BLOCK_KEY))

        connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/carousel",
        status_code=status.HTTP_303_SEE_OTHER
    )

# === /inline project and carousel media admin ===


# === home carousel public api ===

@router.get("/api/home-carousel")
async def api_home_carousel():
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT
            id,
            media_type,
            title,
            alt_text,
            file_path,
            poster_path,
            original_filename,
            sort_order,
            target_key
        FROM media_files
        WHERE owner_type = 'visual'
          AND block_key = 'home_carousel'
          AND is_active = TRUE
        ORDER BY
            sort_order ASC,
            created_at ASC,
            id ASC;
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    media = []

    for row in rows:
        media.append({
            "id": row["id"],
            "media_type": row["media_type"],
            "title": row["title"],
            "alt_text": row["alt_text"],
            "file_path": row["file_path"],
            "poster_path": row["poster_path"],
            "original_filename": row["original_filename"],
            "sort_order": row["sort_order"],
            "target_key": row.get("target_key")
        })

    return {
        "media": media
    }

# === /home carousel public api ===


# === carousel cards admin ===

# ATS_CAROUSEL_SAVE_CATEGORY_SYNC_V1

CAROUSEL_TARGET_CATEGORY_SLUGS = {
    "tattoo": "tattoo",
    "paintings": "paintings",

    "japanese": "tattoo-japanese",
    "graphics": "tattoo-graphics",
    "engraving": "tattoo-engraving",
    "traditional": "tattoo-traditional",
    "dotwork": "tattoo-dotwork",
    "free_sketch": "free-sketches",

    "canvas": "paintings-canvas",
    "skateboards": "paintings-skateboards",
    "plywood": "paintings-plywood",

    "tattoo-gift-certificate": "tattoo-gift-certificate",
    "stickerpack": "stickerpack",
    "tattoo-aftercare-kit": "tattoo-aftercare-kit",
    "tshirts": "tshirts",
}


@router.post("/admin/carousel/cards/{target_key}/edit")
async def admin_carousel_card_edit(
    target_key: str,
    label: str = Form(...),
    subtitle: str = Form(""),
    link_url: str = Form(""),
    sort_order: int = Form(100),
    is_active: Optional[str] = Form(None),
    admin: str = Depends(verify_admin)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    clean_label = label.strip()
    clean_subtitle = subtitle.strip()
    clean_link = link_url.strip()
    active = bool(is_active)

    cursor.execute("""
        UPDATE carousel_cards
        SET
            label = %s,
            subtitle = NULLIF(%s, ''),
            link_url = NULLIF(%s, ''),
            sort_order = %s,
            is_active = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE target_key = %s;
    """, (
        clean_label,
        clean_subtitle,
        clean_link,
        sort_order,
        active,
        target_key
    ))

    category_slug = CAROUSEL_TARGET_CATEGORY_SLUGS.get(
        target_key
    )

    if category_slug:
        category_title = clean_label

        if target_key == "tattoo" and clean_subtitle:
            category_title = (
                f"{clean_subtitle} {clean_label}"
            ).strip()

        cursor.execute("""
            UPDATE project_categories
            SET
                title = %s,
                is_active = %s
            WHERE slug = %s;
        """, (
            category_title,
            active,
            category_slug
        ))

        # ATS_CAROUSEL_ORDER_NORMALIZE_V2
        # carousel_cards.sort_order — глобальный порядок админки.
        # project_categories.display_order — локальный порядок
        # внутри конкретной группы. Поэтому прямое копирование
        # 40 -> 40, 50 -> 50 и т.д. здесь неверно.

        order_groups = [
            (
                1,
                {
                    "japanese": "tattoo-japanese",
                    "graphics": "tattoo-graphics",
                    "engraving": "tattoo-engraving",
                    "traditional": "tattoo-traditional",
                    "dotwork": "tattoo-dotwork",
                    "free_sketch": "free-sketches",
                },
            ),
            (
                1,
                {
                    "canvas": "paintings-canvas",
                    "skateboards": "paintings-skateboards",
                    "plywood": "paintings-plywood",
                },
            ),
            (
                31,
                {
                    "tattoo-gift-certificate":
                        "tattoo-gift-certificate",
                    "stickerpack":
                        "stickerpack",
                    "tattoo-aftercare-kit":
                        "tattoo-aftercare-kit",
                    "tshirts":
                        "tshirts",
                },
            ),
        ]

        for base_order, key_to_slug in order_groups:
            target_keys = list(key_to_slug.keys())

            cursor.execute("""
                SELECT target_key
                FROM carousel_cards
                WHERE target_key = ANY(%s)
                ORDER BY sort_order ASC, id ASC;
            """, (target_keys,))

            ordered_keys = [
                row[0]
                for row in cursor.fetchall()
            ]

            for offset, ordered_key in enumerate(
                ordered_keys
            ):
                ordered_slug = key_to_slug.get(
                    ordered_key
                )

                if not ordered_slug:
                    continue

                cursor.execute("""
                    UPDATE project_categories
                    SET display_order = %s
                    WHERE slug = %s;
                """, (
                    base_order + offset,
                    ordered_slug
                ))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/carousel",
        status_code=status.HTTP_303_SEE_OTHER
    )


# ATS_CAROUSEL_CERTIFICATE_SETTINGS_SAVE_V1
@router.post("/admin/carousel/certificate-settings")
async def admin_carousel_certificate_settings_save(
    certificate_info_title: str = Form(""),
    certificate_validity_text: str = Form(""),
    certificate_min_nominal: str = Form("5000"),
    certificate_nominal_text: str = Form(""),
    certificate_partial_payment_text: str = Form(""),
    certificate_single_use_text: str = Form(""),
    certificate_button_text: str = Form(""),
    admin: str = Depends(verify_admin),
):
    try:
        min_nominal = int(
            certificate_min_nominal.strip()
        )
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Минимальный номинал должен быть числом",
        )

    if min_nominal < 1:
        raise HTTPException(
            status_code=400,
            detail="Минимальный номинал должен быть больше нуля",
        )

    settings_to_save = {
        "certificate_info_title":
            certificate_info_title.strip(),

        "certificate_validity_text":
            certificate_validity_text.strip(),

        "certificate_min_nominal":
            str(min_nominal),

        "certificate_nominal_text":
            certificate_nominal_text.strip(),

        "certificate_partial_payment_text":
            certificate_partial_payment_text.strip(),

        "certificate_single_use_text":
            certificate_single_use_text.strip(),

        "certificate_button_text":
            certificate_button_text.strip(),
    }

    for key, default_value in (
        CERTIFICATE_SETTINGS_DEFAULTS.items()
    ):
        if not settings_to_save.get(key):
            settings_to_save[key] = default_value

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        for setting_key, setting_value in (
            settings_to_save.items()
        ):
            cursor.execute(
                """
                INSERT INTO site_settings (
                    setting_key,
                    setting_value
                )
                VALUES (%s, %s)
                ON CONFLICT (setting_key)
                DO UPDATE
                SET setting_value =
                    EXCLUDED.setting_value;
                """,
                (
                    setting_key,
                    setting_value,
                ),
            )

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return RedirectResponse(
        url="/admin/carousel#certificate-settings",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# === /carousel cards admin ===


# === category media api ===
