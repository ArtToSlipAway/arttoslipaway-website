import mimetypes
import psycopg2
import psycopg2.extras
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from app.paths import APP_DIR, STATIC_DIR, UPLOADS_DIR
from fastapi.responses import FileResponse
from app.db import get_db_connection
from app.views import templates
from app.certificates import CERTIFICATE_SETTINGS_DEFAULTS, get_certificate_settings
from fastapi import APIRouter

router = APIRouter()

@router.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    return FileResponse(STATIC_DIR / "robots.txt", media_type="text/plain")


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml():
    from xml.sax.saxutils import escape

    base_url = "https://arttoslipaway.art"

    static_urls = [
        ("/", "1.0"),
        ("/projects", "0.9"),
        ("/request", "0.8"),
        ("/privacy", "0.3"),
        ("/consent", "0.3"),
        ("/terms", "0.3"),
        ("/cookies", "0.3"),
    ]

    connection = get_db_connection()
    cursor = connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    try:
        cursor.execute("""
            SELECT slug
            FROM project_categories
            WHERE is_active = TRUE
              AND parent_slug IS NULL
            ORDER BY display_order, id;
        """)

        main_projects = cursor.fetchall()

        cursor.execute("""
            SELECT slug
            FROM project_categories
            WHERE is_active = TRUE
              AND parent_slug IS NOT NULL
            ORDER BY
                category_group,
                parent_slug,
                display_order,
                id;
        """)

        child_categories = cursor.fetchall()

        cursor.execute("""
            SELECT slug
            FROM projects
            WHERE status NOT IN ('hidden', 'draft')
              AND slug IS NOT NULL
              AND slug <> ''
            ORDER BY id;
        """)

        public_projects = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    urls = list(static_urls)

    for row in main_projects:
        urls.append(
            (
                f"/categories/{row['slug']}",
                "0.9",
            )
        )

    for row in child_categories:
        urls.append(
            (
                f"/categories/{row['slug']}",
                "0.8",
            )
        )

    for row in public_projects:
        urls.append(
            (
                f"/projects/{row['slug']}",
                "0.7",
            )
        )

    unique_urls = []
    seen = set()

    for url_path, priority in urls:
        if url_path in seen:
            continue

        seen.add(url_path)
        unique_urls.append(
            (url_path, priority)
        )

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for url_path, priority in unique_urls:
        location = escape(
            f"{base_url}{url_path}"
        )

        xml_lines.extend([
            "  <url>",
            f"    <loc>{location}</loc>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ])

    xml_lines.append("</urlset>")

    newline = chr(10)
    xml = newline.join(xml_lines) + newline

    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Cache-Control": "public, max-age=3600"
        },
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
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
        WHERE is_active = TRUE
        ORDER BY
            CASE WHEN parent_slug IS NULL THEN 0 ELSE 1 END,
            category_group,
            parent_slug,
            display_order,
            id;
    """)

    categories = cursor.fetchall()

    cursor.execute("""
        SELECT setting_key, setting_value
        FROM site_settings;
    """)

    rows = cursor.fetchall()
    settings = {row["setting_key"]: row["setting_value"] for row in rows}

    # ATS_HOME_CAROUSEL_CONTEXT_V1
    cursor.execute("""
        SELECT
            target_key,
            label,
            subtitle,
            link_url,
            sort_order,
            is_active
        FROM carousel_cards
        ORDER BY sort_order, id;
    """)

    carousel_rows = cursor.fetchall()

    carousel_cards = {
        row["target_key"]: row
        for row in carousel_rows
    }

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ArtToSlipAway",
            "categories": categories,
            "settings": settings,
            "carousel_cards": carousel_cards
        }
    )


@router.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
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
        WHERE is_active = TRUE
        ORDER BY
            CASE WHEN parent_slug IS NULL THEN 0 ELSE 1 END,
            category_group,
            parent_slug,
            display_order,
            id;
    """)

    categories = cursor.fetchall()

    cursor.execute("""
        SELECT setting_key, setting_value
        FROM site_settings
        WHERE setting_key LIKE 'portfolio_%';
    """)
    portfolio_settings = {
        row["setting_key"]: row["setting_value"]
        for row in cursor.fetchall()
    }

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "title": "Портфолио",
            "categories": categories,
            "settings": portfolio_settings
        }
    )


@router.get("/projects/{slug}", response_class=HTMLResponse)
async def project_detail(request: Request, slug: str):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT
            id,
            title,
            slug,
            project_type,
            status,
            short_description,
            full_description,
            style,
            format,
            price,
            image_url,
            created_at
        FROM projects
        WHERE slug = %s
          AND status NOT IN ('hidden', 'draft')
        LIMIT 1;
    """, (slug,))

    project = cursor.fetchone()
    cursor.close()
    connection.close()

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "title": project["title"],
            "project": project
        }
    )


@router.get("/thanks", response_class=HTMLResponse)
async def thanks(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="thanks.html",
        context={"title": "Заявка отправлена"}
    )


@router.get("/media-files/{media_id}/{variant}")
async def public_media_file(
    media_id: int,
    variant: str,
):
    from pathlib import Path
    import mimetypes

    if variant not in {"file", "poster"}:
        raise HTTPException(
            status_code=404,
            detail="Файл не найден",
        )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                file_path,
                poster_path,
                mime_type,
                is_active
            FROM media_files
            WHERE id = %s
            LIMIT 1;
        """, (media_id,))

        media = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if not media or not media[3]:
        raise HTTPException(
            status_code=404,
            detail="Файл не найден",
        )

    selected_path = (
        media[1]
        if variant == "poster"
        else media[0]
    )

    if not selected_path:
        raise HTTPException(
            status_code=404,
            detail="Файл не найден",
        )

    app_root = APP_DIR.resolve()
    uploads_root = UPLOADS_DIR.resolve()

    absolute_path = (
        app_root
        / selected_path.lstrip("/")
    ).resolve()

    try:
        absolute_path.relative_to(
            uploads_root
        )
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Недопустимый путь",
        )

    if not absolute_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Файл отсутствует",
        )

    if variant == "file":
        content_type = (
            media[2]
            or mimetypes.guess_type(
                absolute_path.name
            )[0]
            or "application/octet-stream"
        )
    else:
        content_type = (
            mimetypes.guess_type(
                absolute_path.name
            )[0]
            or "application/octet-stream"
        )

    return FileResponse(
        path=str(absolute_path),
        media_type=content_type,
        headers={
            "Cache-Control": (
                "public, max-age=3600"
            )
        },
    )


@router.get("/categories/{slug}", response_class=HTMLResponse)
async def category_detail(request: Request, slug: str):
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
        WHERE slug = %s
          AND is_active = TRUE
        LIMIT 1;
    """, (slug,))

    category = cursor.fetchone()

    if not category:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Категория не найдена")

    certificate_model = None

    # ATS_CATEGORY_CERTIFICATE_SETTINGS_V1
    certificate_settings = dict(
        CERTIFICATE_SETTINGS_DEFAULTS
    )

    if slug == "tattoo-gift-certificate":
        cursor.execute("""
            SELECT
                id,
                title,
                alt_text,
                file_path,
                poster_path,
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
              AND is_active = TRUE
            ORDER BY id DESC
            LIMIT 1;
        """, (category["id"],))

        certificate_model = cursor.fetchone()

        certificate_settings = (
            get_certificate_settings(
                connection
            )
        )

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
        WHERE parent_slug = %s
          AND is_active = TRUE
        ORDER BY display_order ASC, id ASC;
    """, (slug,))

    children = cursor.fetchall()

    category_slugs = [slug]

    for child in children:
        category_slugs.append(child["slug"])

    fallback_type_mapping = {
        "tattoo": ["tattoo", "sketch"],
        "free-sketches": ["sketch"],
        "paintings": ["canvas", "skate", "plywood"],
        "paintings-canvas": ["canvas"],
        "paintings-skateboards": ["skate"],
        "paintings-plywood": ["plywood"]
    }

    fallback_types = fallback_type_mapping.get(slug, [])

    if fallback_types:
        cursor.execute("""
            SELECT
                id,
                title,
                slug,
                project_type,
                category_slug,
                status,
                short_description,
                style,
                format,
                price,
                image_url,
                display_order
            FROM projects
            WHERE status NOT IN ('hidden', 'draft')
              AND (
                    category_slug = ANY(%s)
                    OR (
                        (category_slug IS NULL OR category_slug = '')
                        AND project_type = ANY(%s)
                    )
              )
            ORDER BY display_order ASC, created_at DESC;
        """, (category_slugs, fallback_types))
    else:
        cursor.execute("""
            SELECT
                id,
                title,
                slug,
                project_type,
                category_slug,
                status,
                short_description,
                style,
                format,
                price,
                image_url,
                display_order
            FROM projects
            WHERE status NOT IN ('hidden', 'draft')
              AND category_slug = ANY(%s)
            ORDER BY display_order ASC, created_at DESC;
        """, (category_slugs,))

    projects = cursor.fetchall()

    # ATS_JAPANESE_MODEL_SHOWCASE_V1_START
    japanese_models = []

    if slug == "tattoo-japanese":
        cursor.execute("""
            SELECT
                mf.id,
                COALESCE(
                    NULLIF(mf.title, ''),
                    NULLIF(p.title, ''),
                    '3D-модель'
                ) AS display_title,
                mf.alt_text,
                mf.file_path,
                mf.poster_path,
                mf.mime_type,
                mf.file_size,
                mf.sort_order,
                mf.updated_at,
                p.id AS project_id,
                p.title AS project_title,
                p.slug AS project_slug,
                p.category_slug
            FROM media_files mf
            LEFT JOIN projects p
              ON p.id = mf.owner_id
            WHERE mf.owner_type = 'free_sketch'
              AND mf.media_type = 'model'
              AND mf.is_active = TRUE
            ORDER BY
                CASE
                    WHEN p.category_slug = %s THEN 0
                    ELSE 1
                END,
                mf.sort_order ASC,
                mf.id ASC;
        """, (slug,))

        japanese_models = cursor.fetchall()
    # ATS_JAPANESE_MODEL_SHOWCASE_V1_END

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="category_detail.html",
        context={
            "title": category["title"],
            "category": category,
            "children": children,
            "projects": projects,
            "japanese_models": japanese_models,
            "certificate_model": certificate_model,
            "certificate_settings": certificate_settings
        }
    )


@router.get("/api/category-media/{slug}")
async def api_category_media(slug: str):
    # ATS_CATEGORY_MEDIA_FILTER_V3
    aliases = {
        "free_sketch": "free-sketches",
        "free-sketch": "free-sketches",
    }

    canonical_slug = aliases.get(slug, slug)

    connection = get_db_connection()

    cursor = connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    try:
        cursor.execute(
            """
            SELECT slug
            FROM project_categories
            WHERE slug = %s
              AND is_active = TRUE
            LIMIT 1;
            """,
            (canonical_slug,),
        )

        category = cursor.fetchone()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Категория не найдена",
            )

        if canonical_slug == "free-sketches":
            free_sketch_keys = [
                "free-sketches",
                "free_sketch",
                "free-sketch",
            ]

            cursor.execute(
                """
                SELECT
                    mf.id,
                    mf.owner_type,
                    mf.owner_id,
                    mf.block_key,
                    mf.media_type,
                    mf.title,
                    mf.alt_text,
                    mf.file_path,
                    mf.poster_path,
                    mf.original_filename,
                    mf.mime_type,
                    mf.file_size,
                    mf.sort_order,
                    mf.target_key,
                    mf.created_at,
                    mf.updated_at,
                    p.slug AS project_slug,
                    p.title AS project_title,
                    p.category_slug
                FROM media_files mf
                LEFT JOIN projects p
                  ON p.id = mf.owner_id
                WHERE mf.is_active = TRUE
                  AND (
                        mf.owner_type = 'free_sketch'
                     OR mf.block_key = 'free_sketch_gallery'
                     OR mf.target_key = ANY(%s)
                  )
                ORDER BY
                    mf.sort_order ASC,
                    mf.created_at ASC,
                    mf.id ASC;
                """,
                (free_sketch_keys,),
            )

        else:
            cursor.execute(
                """
                SELECT slug
                FROM project_categories
                WHERE parent_slug = %s
                  AND is_active = TRUE
                ORDER BY display_order ASC, id ASC;
                """,
                (canonical_slug,),
            )

            category_slugs = [
                canonical_slug,
                *[
                    row["slug"]
                    for row in cursor.fetchall()
                ],
            ]

            cursor.execute(
                """
                SELECT
                    mf.id,
                    mf.owner_type,
                    mf.owner_id,
                    mf.block_key,
                    mf.media_type,
                    mf.title,
                    mf.alt_text,
                    mf.file_path,
                    mf.poster_path,
                    mf.original_filename,
                    mf.mime_type,
                    mf.file_size,
                    mf.sort_order,
                    mf.target_key,
                    mf.created_at,
                    mf.updated_at,
                    p.slug AS project_slug,
                    p.title AS project_title,
                    p.category_slug
                FROM media_files mf
                LEFT JOIN projects p
                  ON p.id = mf.owner_id
                WHERE mf.is_active = TRUE
                  AND (
                        mf.target_key = ANY(%s)
                     OR (
                            p.id IS NOT NULL
                        AND p.category_slug = ANY(%s)
                        AND p.status NOT IN (
                            'hidden',
                            'draft'
                        )
                        AND mf.owner_type = 'project'
                     )
                  )
                ORDER BY
                    mf.sort_order ASC,
                    mf.created_at ASC,
                    mf.id ASC;
                """,
                (
                    category_slugs,
                    category_slugs,
                ),
            )

        media = cursor.fetchall()

        return {
            "slug": canonical_slug,
            "media": media,
        }

    finally:
        cursor.close()
        connection.close()
