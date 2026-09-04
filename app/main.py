import html
from urllib.parse import quote
import time
import threading
import base64
import hashlib
import hmac
import os
import secrets
from urllib.parse import urlparse
import uuid
import mimetypes
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.paths import APP_DIR, ENV_PATH, PROJECT_ROOT, STATIC_DIR, TEMPLATES_DIR, UPLOADS_DIR
from app.upload_core import (
    REFERENCE_UPLOAD_EXTENSIONS,
    save_upload_file,
)

load_dotenv(ENV_PATH)

BASE_DIR = PROJECT_ROOT
UPLOAD_DIR = UPLOADS_DIR

app = FastAPI(title="ArtToSlipAway")
security = HTTPBasic(auto_error=False)


# === admin CSRF origin guard ===
ADMIN_CSRF_ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "ADMIN_CSRF_ALLOWED_ORIGINS",
        (
            "https://arttoslipaway.art,"
            "https://www.arttoslipaway.art,"
            "http://127.0.0.1:8000,"
            "http://localhost:8000"
        ),
    ).split(",")
    if origin.strip()
}

ADMIN_CSRF_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _ats_same_origin_header_allowed(value: str) -> bool:
    if not value:
        return False

    try:
        parsed = urlparse(value)
    except Exception:
        return False

    scheme = (parsed.scheme or "").lower()
    netloc = (parsed.netloc or "").lower()

    return f"{scheme}://{netloc}" in ADMIN_CSRF_ALLOWED_ORIGINS


@app.middleware("http")
async def admin_csrf_origin_guard(request: Request, call_next):
    path = request.url.path or ""

    if request.method.upper() in ADMIN_CSRF_METHODS and path.startswith("/admin"):
        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")

        if origin:
            if not _ats_same_origin_header_allowed(origin):
                return PlainTextResponse("Forbidden: invalid admin origin", status_code=403)
        elif referer:
            if not _ats_same_origin_header_allowed(referer):
                return PlainTextResponse("Forbidden: invalid admin referer", status_code=403)
        else:
            return PlainTextResponse("Forbidden: missing admin origin", status_code=403)

    return await call_next(request)

# === /admin CSRF origin guard ===

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

from fastapi.responses import FileResponse, Response


@app.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    return FileResponse(STATIC_DIR / "robots.txt", media_type="text/plain")


@app.get("/sitemap.xml", include_in_schema=False)
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


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


@app.get("/", response_class=HTMLResponse)
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


@app.get("/projects", response_class=HTMLResponse)
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


@app.get("/projects/{slug}", response_class=HTMLResponse)
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



# ATS_CERTIFICATE_SITE_SETTINGS_V1

CERTIFICATE_SETTINGS_DEFAULTS = {
    "certificate_info_title":
        "Информация о сертификате",

    "certificate_validity_text":
        "Срок действия сертификата — 6 месяцев с момента приобретения.",

    "certificate_min_nominal":
        "5000",

    "certificate_nominal_text":
        "Минимальный номинал равен минимальной стоимости сеанса —",

    "certificate_partial_payment_text":
        "Сертификат можно использовать для частичной оплаты сеанса.",

    "certificate_single_use_text":
        "Сертификатом можно воспользоваться один раз на протяжении срока его действия.",

    "certificate_button_text":
        "Приобрести сертификат",
}


def get_certificate_settings(connection):
    settings = dict(
        CERTIFICATE_SETTINGS_DEFAULTS
    )

    settings_cursor = connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    try:
        settings_cursor.execute(
            """
            SELECT
                setting_key,
                setting_value
            FROM site_settings
            WHERE setting_key = ANY(%s);
            """,
            (
                list(
                    CERTIFICATE_SETTINGS_DEFAULTS.keys()
                ),
            ),
        )

        for row in settings_cursor.fetchall():
            value = row["setting_value"]

            if value is not None:
                settings[row["setting_key"]] = value

    finally:
        settings_cursor.close()

    return settings


def get_certificate_min_nominal(settings):
    try:
        value = int(
            str(
                settings.get(
                    "certificate_min_nominal",
                    "5000",
                )
            ).strip()
        )
    except (TypeError, ValueError):
        value = 5000

    if value < 1:
        value = 5000

    return value


@app.get("/request", response_class=HTMLResponse)
async def request_form(
    request: Request,
    project: Optional[str] = None,
    service: Optional[str] = None,
    category: Optional[str] = None,
    source: Optional[str] = "site",
    city: Optional[str] = None,
    media_id: Optional[int] = None,
    sketch: Optional[str] = None
):
    selected_project = None
    selected_media = None
    selected_sketch_title = sketch or ""

    # ATS_REQUEST_CERTIFICATE_SETTINGS_V1
    certificate_settings = dict(
        CERTIFICATE_SETTINGS_DEFAULTS
    )

    if category == "tattoo-gift-certificate":
        settings_connection = get_db_connection()

        try:
            certificate_settings = (
                get_certificate_settings(
                    settings_connection
                )
            )
        finally:
            settings_connection.close()

    certificate_min_nominal = (
        get_certificate_min_nominal(
            certificate_settings
        )
    )

    if project:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT id, title, slug, project_type, status, short_description, style, format, price
            FROM projects
            WHERE slug = %s
              AND status NOT IN ('hidden', 'draft')
            LIMIT 1;
        """, (project,))

        selected_project = cursor.fetchone()

        cursor.close()
        connection.close()

    if media_id:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT
                id,
                title,
                media_type,
                file_path,
                poster_path,
                alt_text,
                original_filename
            FROM media_files
            WHERE id = %s
              AND is_active = TRUE
              AND (
                    owner_type = 'free_sketch'
                 OR block_key = 'free_sketch_gallery'
                 OR target_key IN ('free_sketch', 'free-sketches', 'free-sketch')
              )
            LIMIT 1;
        """, (media_id,))

        selected_media = cursor.fetchone()

        cursor.close()
        connection.close()

        if selected_media:
            selected_sketch_title = (
                selected_media.get("title")
                or selected_media.get("original_filename")
                or selected_sketch_title
            )

    return templates.TemplateResponse(
        request=request,
        name="request.html",
        context={
            "title": "Заявка на проект",
            "selected_project": selected_project,
            "selected_service": service or "",
            "selected_category": category or "",
            "certificate_min_nominal": certificate_min_nominal,
            "lead_source": source or "site",
            "selected_city": city or "",
            "selected_media_id": media_id,
            "selected_media": selected_media,
            "selected_sketch_title": selected_sketch_title
        }
    )


@app.post("/request")
async def create_request(
    request: Request,
    name: str = Form(...),
    contact: str = Form(...),
    contact_method: str = Form("telegram"),
    service_type: str = Form("tattoo"),
    request_type: str = Form(""),
    city: str = Form(""),
    body_place: str = Form(""),
    approximate_size: str = Form(""),
    style_preference: str = Form(""),
    product_format: str = Form(""),
    budget_range: str = Form(""),
    preferred_dates: str = Form(""),
    idea: str = Form(""),
    message: str = Form(""),
    lead_source: str = Form("site"),
    entry_page: str = Form(""),
    project_id: Optional[int] = Form(None),
    category_slug: str = Form(""),
    selected_media_id: str = Form(""),
    selected_sketch_title: str = Form(""),
    personal_data_agreement: Optional[str] = Form(None),
    reference_files: Optional[List[UploadFile]] = File(None)
):
    if not personal_data_agreement:
        raise HTTPException(status_code=400, detail="Нужно согласие на обработку заявки")

    # ATS_CERTIFICATE_NOMINAL_VALIDATE_V1
    # ATS_CERTIFICATE_NOMINAL_DYNAMIC_V1
    if category_slug.strip() == "tattoo-gift-certificate":

        settings_connection = get_db_connection()

        try:
            certificate_settings = (
                get_certificate_settings(
                    settings_connection
                )
            )
        finally:
            settings_connection.close()

        certificate_min_nominal = (
            get_certificate_min_nominal(
                certificate_settings
            )
        )

        try:
            certificate_nominal = int(
                str(budget_range).strip()
            )
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Укажи корректный номинал сертификата"
                ),
            )

        if certificate_nominal < certificate_min_nominal:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Минимальный номинал сертификата — "
                    f"{certificate_min_nominal} ₽"
                ),
            )

        budget_range = str(
            certificate_nominal
        )

    selected_media_id_value = None

    if str(selected_media_id).strip():
        try:
            selected_media_id_value = int(str(selected_media_id).strip())
        except ValueError:
            selected_media_id_value = None

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    project_interest = service_type

    cursor.execute("""
        INSERT INTO leads (
            name,
            contact,
            contact_method,
            project_interest,
            body_place,
            approximate_size,
            idea,
            message,
            personal_data_agreement,
            lead_status,
            admin_note,
            lead_source,
            entry_page,
            project_id,
            category_slug,
            service_type,
            request_type,
            city,
            style_preference,
            is_coverup,
            product_format,
            deadline,
            budget_range,
            preferred_dates,
            selected_media_id,
            selected_sketch_title,
            updated_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            'new', '',
            %s, %s, %s, %s, %s, %s, %s, %s, FALSE, %s, '', %s, %s, %s, %s,
            CURRENT_TIMESTAMP
        )
        RETURNING id;
    """, (
        name.strip(),
        contact.strip(),
        contact_method.strip(),
        project_interest.strip(),
        body_place.strip(),
        approximate_size.strip(),
        idea.strip(),
        message.strip(),
        True,
        lead_source.strip(),
        entry_page.strip(),
        project_id,
        category_slug.strip(),
        service_type.strip(),
        request_type.strip(),
        city.strip(),
        style_preference.strip(),
        product_format.strip(),
        budget_range.strip(),
        preferred_dates.strip(),
        selected_media_id_value,
        selected_sketch_title.strip()
    ))

    lead = cursor.fetchone()
    lead_id = lead["id"]

    if reference_files:
        for uploaded_file in reference_files:
            if not uploaded_file or not uploaded_file.filename:
                continue

            file_path = await save_upload_file(
                uploaded_file,
                allowed_extensions=REFERENCE_UPLOAD_EXTENSIONS,
            )

            if not file_path:
                continue

            cursor.execute("""
                INSERT INTO lead_files (
                    lead_id,
                    file_path,
                    original_filename,
                    file_type
                )
                VALUES (%s, %s, %s, %s);
            """, (
                lead_id,
                file_path,
                uploaded_file.filename,
                uploaded_file.content_type or ""
            ))

    connection.commit()
    cursor.close()
    connection.close()

    # ATS_LEAD_EMAIL_NOTIFY_START
    try:
        from app.mail_sender import send_new_lead_email
        send_new_lead_email(
            lead_id=lead_id,
            lead_data=dict(locals()),
            is_test=False,
        )
    except Exception:
        import logging
        logging.exception("Failed to send new lead email notification")
    # ATS_LEAD_EMAIL_NOTIFY_END

    return RedirectResponse(
        url=f"/thanks?lead_id={lead_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/thanks", response_class=HTMLResponse)
async def thanks(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="thanks.html",
        context={"title": "Заявка отправлена"}
    )


# === admin cms hub ===


# === extracted admin auth ===
from app.auth import verify_admin
# === /extracted admin auth ===

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    stats = {
        "leads_total": 0,
        "leads_new": 0,
        "projects_total": 0,
        "categories_total": 0,
        "city_slots_total": 0,
        "media_total": 0,
        "images_total": 0,
        "videos_total": 0,
        "models_total": 0,
    }

    cursor.execute("SELECT COUNT(*) AS count FROM leads;")
    stats["leads_total"] = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM leads WHERE lead_status = 'new';")
    stats["leads_new"] = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM projects;")
    stats["projects_total"] = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM project_categories;")
    stats["categories_total"] = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM city_slots;")
    stats["city_slots_total"] = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM media_files;")
    stats["media_total"] = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM media_files WHERE media_type = 'image';")
    stats["images_total"] = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM media_files WHERE media_type = 'video';")
    stats["videos_total"] = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM media_files WHERE media_type = 'model';")
    stats["models_total"] = cursor.fetchone()["count"]

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "title": "Панель управления",
            "stats": stats
        }
    )


# === admin media manager ===


# === extracted media core ===
from app.media_core import (
    MEDIA_ROOT,
    MEDIA_PUBLIC_PREFIX,
    detect_media_type,
    save_media_file,
    save_poster_file,
    public_media_path_to_file,
)
# === /extracted media core ===

@app.get("/admin/projects", response_class=HTMLResponse)
async def admin_projects(
    request: Request,
    type_filter: str = "",
    admin: str = Depends(verify_admin)
):
    allowed_types = {
        "tattoo",
        "canvas",
        "skate",
        "sketch",
        "merch"
    }

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if type_filter in allowed_types:
        cursor.execute("""
            SELECT id, title, slug, project_type, category_slug, status, style, format, price, image_url, display_order, created_at
            FROM projects
            WHERE project_type = %s
            ORDER BY display_order ASC, created_at DESC;
        """, (type_filter,))
    else:
        cursor.execute("""
            SELECT id, title, slug, project_type, category_slug, status, style, format, price, image_url, display_order, created_at
            FROM projects
            ORDER BY display_order ASC, created_at DESC;
        """)

    projects = cursor.fetchall()
    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_projects.html",
        context={
            "title": "Проекты",
            "projects": projects,
            "type_filter": type_filter
        }
    )


@app.get("/admin/projects/new", response_class=HTMLResponse)
async def admin_project_new(request: Request, admin: str = Depends(verify_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin_project_new.html",
        context={"title": "Добавить проект"}
    )


@app.post("/admin/projects/new")
async def admin_project_create(
    admin: str = Depends(verify_admin),
    title: str = Form(...),
    slug: str = Form(...),
    project_type: str = Form(...),
    status: str = Form(...),
    short_description: str = Form(""),
    full_description: str = Form(""),
    style: str = Form(""),
    format: str = Form(""),
    price: str = Form(""),
    external_image_url: str = Form(""),
    image_file: Optional[UploadFile] = File(None),

    display_order: int = Form(100),
    category_slug: str = Form(""),
    is_featured: str = Form(None),
):
    # ATS_PROJECT_CATEGORY_LINKAGE_V2
    featured = is_featured == "yes"

    uploaded_image_url = await save_upload_file(
        image_file
    )

    final_image_url = (
        uploaded_image_url
        or external_image_url.strip()
        or None
    )

    category_slug_value = (
        category_slug.strip()
        or None
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if category_slug_value:
            cursor.execute(
                """
                SELECT 1
                FROM project_categories
                WHERE slug = %s
                LIMIT 1;
                """,
                (category_slug_value,),
            )

            if not cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Выбранная категория не существует",
                )

        cursor.execute(
            """
            INSERT INTO projects (
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
                display_order,
                category_slug,
                is_featured
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            );
            """,
            (
                title.strip(),
                slug.strip(),
                project_type.strip(),
                status.strip(),
                short_description.strip(),
                full_description.strip(),
                style.strip(),
                format.strip(),
                price.strip(),
                final_image_url,
                display_order,
                category_slug_value,
                featured,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return RedirectResponse(
        url="/admin/projects",
        status_code=303
    )


@app.get("/admin/projects/{project_id}/edit", response_class=HTMLResponse)
async def admin_project_edit(request: Request, project_id: int, admin: str = Depends(verify_admin)):
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
            display_order,
            is_featured
        FROM projects
        WHERE id = %s
        LIMIT 1;
    """, (project_id,))

    project = cursor.fetchone()
    cursor.close()
    connection.close()

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    return templates.TemplateResponse(
        request=request,
        name="admin_project_edit.html",
        context={
            "title": "Редактировать проект",
            "project": project
        }
    )


@app.post("/admin/projects/{project_id}/edit")
async def admin_project_update(
    project_id: int,
    admin: str = Depends(verify_admin),
    title: str = Form(...),
    slug: str = Form(...),
    project_type: str = Form(...),
    status: str = Form(...),
    short_description: str = Form(""),
    full_description: str = Form(""),
    style: str = Form(""),
    format: str = Form(""),
    price: str = Form(""),
    external_image_url: str = Form(""),
    image_file: Optional[UploadFile] = File(None),
    display_order: int = Form(100),
    category_slug: str = Form(""),
    is_featured: str = Form(None),
):
    # ATS_PROJECT_CATEGORY_LINKAGE_V2
    featured = is_featured == "yes"

    uploaded_image_url = await save_upload_file(
        image_file
    )

    category_slug_value = (
        category_slug.strip()
        or None
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT image_url
            FROM projects
            WHERE id = %s
            LIMIT 1;
            """,
            (project_id,),
        )

        current_project = cursor.fetchone()

        if not current_project:
            raise HTTPException(
                status_code=404,
                detail="Проект не найден",
            )

        current_image_url = current_project[0]

        final_image_url = (
            uploaded_image_url
            or external_image_url.strip()
            or current_image_url
        )

        if category_slug_value:
            cursor.execute(
                """
                SELECT 1
                FROM project_categories
                WHERE slug = %s
                LIMIT 1;
                """,
                (category_slug_value,),
            )

            if not cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Выбранная категория не существует",
                )

        cursor.execute(
            """
            UPDATE projects
            SET
                title = %s,
                slug = %s,
                project_type = %s,
                status = %s,
                short_description = %s,
                full_description = %s,
                style = %s,
                format = %s,
                price = %s,
                image_url = %s,
                display_order = %s,
                category_slug = %s,
                is_featured = %s
            WHERE id = %s;
            """,
            (
                title.strip(),
                slug.strip(),
                project_type.strip(),
                status.strip(),
                short_description.strip(),
                full_description.strip(),
                style.strip(),
                format.strip(),
                price.strip(),
                final_image_url,
                display_order,
                category_slug_value,
                featured,
                project_id,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return RedirectResponse(
        url="/admin/projects",
        status_code=303
    )


@app.post("/admin/projects/{project_id}/category")
async def admin_project_update_category(
    project_id: int,
    category_slug: str = Form(...),
    admin: str = Depends(verify_admin)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE projects
        SET category_slug = %s
        WHERE id = %s;
    """, (category_slug, project_id))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(url="/admin/projects", status_code=303)


@app.post("/admin/projects/{project_id}/order")
async def admin_project_update_order(
    project_id: int,
    display_order: int = Form(...),
    admin: str = Depends(verify_admin)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE projects
        SET display_order = %s
        WHERE id = %s;
    """, (display_order, project_id))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(url="/admin/projects", status_code=303)


@app.post("/admin/projects/{project_id}/hide")
async def admin_project_hide(project_id: int, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE projects SET status = 'hidden' WHERE id = %s;", (project_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return RedirectResponse(url="/admin/projects", status_code=303)


@app.post("/admin/projects/{project_id}/restore")
async def admin_project_restore(project_id: int, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE projects SET status = 'available' WHERE id = %s;", (project_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return RedirectResponse(url="/admin/projects", status_code=303)


@app.post("/admin/projects/{project_id}/delete")
async def admin_project_delete(project_id: int, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM projects WHERE id = %s;", (project_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return RedirectResponse(url="/admin/projects", status_code=303)


@app.get("/admin/visual", response_class=HTMLResponse)
async def admin_visual(request: Request, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT setting_key, setting_value
        FROM site_settings;
    """)

    rows = cursor.fetchall()
    settings = {row["setting_key"]: row["setting_value"] for row in rows}

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_visual.html",
        context={
            "title": "Визуал сайта",
            "settings": settings
        }
    )


@app.post("/admin/visual")
async def admin_visual_update(
    request: Request,
    home_background_url: str = Form(""),
    home_background_file: Optional[UploadFile] = File(None),
    custom_cursor_url: str = Form(""),
    custom_cursor_file: Optional[UploadFile] = File(None),
    portfolio_photo_url: str = Form(""),
    portfolio_photo_file: Optional[UploadFile] = File(None),
    portfolio_lead: str = Form(""),
    portfolio_text_1: str = Form(""),
    portfolio_text_2: str = Form(""),
    portfolio_text_3: str = Form(""),
    portfolio_text_4: str = Form(""),
    portfolio_closing: str = Form(""),
    admin: str = Depends(verify_admin)
):
    background_url = home_background_url.strip() if home_background_url else ""
    cursor_url = custom_cursor_url.strip() if custom_cursor_url else ""
    portfolio_photo = portfolio_photo_url.strip() if portfolio_photo_url else ""

    if home_background_file and home_background_file.filename:
        background_url = await save_upload_file(home_background_file)

    if custom_cursor_file and custom_cursor_file.filename:
        cursor_url = await save_upload_file(custom_cursor_file)

    if portfolio_photo_file and portfolio_photo_file.filename:
        portfolio_photo = await save_upload_file(portfolio_photo_file)

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO site_settings (setting_key, setting_value)
        VALUES ('home_background_url', %s)
        ON CONFLICT (setting_key)
        DO UPDATE SET setting_value = EXCLUDED.setting_value;
    """, (background_url,))

    cursor.execute("""
        INSERT INTO site_settings (setting_key, setting_value)
        VALUES ('custom_cursor_url', %s)
        ON CONFLICT (setting_key)
        DO UPDATE SET setting_value = EXCLUDED.setting_value;
    """, (cursor_url,))

    # === editable portfolio settings v1 ===
    # === editable portfolio photo v1 ===
    portfolio_settings = {
        "portfolio_photo_url": portfolio_photo,
        "portfolio_lead": portfolio_lead.strip(),
        "portfolio_text_1": portfolio_text_1.strip(),
        "portfolio_text_2": portfolio_text_2.strip(),
        "portfolio_text_3": portfolio_text_3.strip(),
        "portfolio_text_4": portfolio_text_4.strip(),
        "portfolio_closing": portfolio_closing.strip(),
    }

    for setting_key, setting_value in portfolio_settings.items():
        cursor.execute("""
            INSERT INTO site_settings (setting_key, setting_value)
            VALUES (%s, %s)
            ON CONFLICT (setting_key)
            DO UPDATE SET setting_value = EXCLUDED.setting_value;
        """, (setting_key, setting_value))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(url="/admin/visual", status_code=303)


@app.get("/admin/categories", response_class=HTMLResponse)
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


@app.get("/admin/categories/{category_id}/edit", response_class=HTMLResponse)
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


@app.post("/admin/categories/{category_id}/edit")
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



# ATS_PUBLIC_MEDIA_FILE_ROUTE_V1
@app.get("/media-files/{media_id}/{variant}")
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


@app.get("/categories/{slug}", response_class=HTMLResponse)
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


# === city slots api ===
# ATS_CITY_SLOTS_PRIVATE_NOTE_V1
# Internal city_slots.note is never exposed by the public API.
# ATS_CITY_SLOTS_INCLUDE_BOOKED_V1


# === GOOGLE CALENDAR SYNC ===

GOOGLE_CALENDAR_FILE = os.getenv(
    "GOOGLE_CALENDAR_CREDENTIALS_FILE",
    str(PROJECT_ROOT / "credentials" / "google-calendar.json"),
)

GOOGLE_CALENDARS = {
    "work": os.getenv("GOOGLE_CALENDAR_WORK_ID", "").strip(),
    "tattoo": os.getenv("GOOGLE_CALENDAR_TATTOO_ID", "").strip(),
}


def get_google_calendar_service():
    credentials_path = Path(GOOGLE_CALENDAR_FILE)
    if not credentials_path.is_file():
        return None

    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )

    return build(
        "calendar",
        "v3",
        credentials=creds
    )


# ATS_CITY_TIME_WINDOWS_V1
#
# Публичное рабочее окно студии:
# 10:00–23:00, Europe/Moscow.
#
# Google Calendar теперь возвращает не просто
# занятые даты, а реальные временные интервалы.
#
# OZON:
#   блокирует только фактическое время смены.
#
# Tattoo:
#   блокирует только события с "тату"/"сеанс"
#   и только фактическое время события.

_SPB_PUBLIC_TZ = timezone(
    timedelta(hours=3)
)

_STUDIO_START_MINUTE = 10 * 60
_STUDIO_END_MINUTE = 23 * 60


def _ats_minutes_label(value):
    hours = value // 60
    minutes = value % 60

    return f"{hours:02d}:{minutes:02d}"


def _ats_copy_busy_intervals(data):
    return {
        day: list(intervals)
        for day, intervals in data.items()
    }


def _ats_add_busy_interval(
    busy,
    day,
    start_minute,
    end_minute
):
    start_minute = max(
        _STUDIO_START_MINUTE,
        int(start_minute)
    )

    end_minute = min(
        _STUDIO_END_MINUTE,
        int(end_minute)
    )

    if end_minute <= start_minute:
        return

    busy.setdefault(
        day.isoformat(),
        []
    ).append(
        (
            start_minute,
            end_minute
        )
    )


def _ats_google_datetime(value):
    if not value:
        return None

    value = value.replace(
        "Z",
        "+00:00"
    )

    return (
        datetime
        .fromisoformat(value)
        .astimezone(_SPB_PUBLIC_TZ)
    )


def _ats_add_google_event(
    busy,
    event
):
    start = event.get(
        "start",
        {}
    )

    end = event.get(
        "end",
        {}
    )

    start_dt_value = start.get(
        "dateTime"
    )

    end_dt_value = end.get(
        "dateTime"
    )

    # Обычное событие с точным временем.
    if start_dt_value and end_dt_value:
        start_dt = _ats_google_datetime(
            start_dt_value
        )

        end_dt = _ats_google_datetime(
            end_dt_value
        )

        if (
            not start_dt
            or not end_dt
            or end_dt <= start_dt
        ):
            return

        current_day = start_dt.date()
        last_day = end_dt.date()

        while current_day <= last_day:

            if current_day == start_dt.date():
                start_minute = (
                    start_dt.hour * 60
                    + start_dt.minute
                )
            else:
                start_minute = 0

            if current_day == end_dt.date():
                end_minute = (
                    end_dt.hour * 60
                    + end_dt.minute
                )
            else:
                end_minute = 24 * 60

            _ats_add_busy_interval(
                busy,
                current_day,
                start_minute,
                end_minute
            )

            current_day += timedelta(
                days=1
            )

        return

    # Google all-day event.
    start_date_value = start.get(
        "date"
    )

    end_date_value = end.get(
        "date"
    )

    if (
        not start_date_value
        or not end_date_value
    ):
        return

    start_day = (
        datetime
        .fromisoformat(start_date_value)
        .date()
    )

    # У Google end.date для all-day exclusive.
    end_day = (
        datetime
        .fromisoformat(end_date_value)
        .date()
    )

    current_day = start_day

    while current_day < end_day:
        _ats_add_busy_interval(
            busy,
            current_day,
            _STUDIO_START_MINUTE,
            _STUDIO_END_MINUTE
        )

        current_day += timedelta(
            days=1
        )


def _ats_merge_intervals(intervals):
    if not intervals:
        return []

    ordered = sorted(
        (
            int(start),
            int(end)
        )
        for start, end in intervals
        if end > start
    )

    merged = []

    for start, end in ordered:

        if (
            not merged
            or start > merged[-1][1]
        ):
            merged.append(
                [start, end]
            )

            continue

        merged[-1][1] = max(
            merged[-1][1],
            end
        )

    return [
        (start, end)
        for start, end in merged
    ]


def get_busy_intervals_from_google():
    configured_calendars = {
        name: calendar_id
        for name, calendar_id in GOOGLE_CALENDARS.items()
        if calendar_id
    }
    if not configured_calendars:
        return {}

    service = get_google_calendar_service()
    if service is None:
        return {}

    busy = {}

    now_utc = datetime.now(
        timezone.utc
    )

    future_utc = (
        now_utc
        + timedelta(days=90)
    )

    for calendar_name, calendar_id in (
        configured_calendars.items()
    ):

        events = (
            service
            .events()
            .list(
                calendarId=calendar_id,
                timeMin=now_utc.isoformat(),
                timeMax=future_utc.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            )
            .execute()
        )

        for event in events.get(
            "items",
            []
        ):

            if (
                event.get("status")
                == "cancelled"
            ):
                continue

            title = (
                event
                .get("summary", "")
                .lower()
            )

            if calendar_name == "work":
                # Любая смена OZON блокирует
                # только своё фактическое время.
                pass

            elif calendar_name == "tattoo":

                if not any(
                    word in title
                    for word in (
                        "сеанс",
                        "тату"
                    )
                ):
                    continue

            else:
                continue

            _ats_add_google_event(
                busy,
                event
            )

    return {
        day: _ats_merge_intervals(
            intervals
        )
        for day, intervals
        in busy.items()
    }


# Google — медленная внешняя часть API.
# Храним результат максимум 60 секунд.

_CITY_SLOTS_GOOGLE_CACHE_TTL = 60.0

_city_slots_google_cache = {
    "expires_at": 0.0,
    "busy_intervals": None,
}

_city_slots_google_cache_lock = (
    threading.Lock()
)


def get_busy_intervals_from_google_cached():
    now = time.monotonic()

    cached = (
        _city_slots_google_cache[
            "busy_intervals"
        ]
    )

    if (
        cached is not None
        and now
        < _city_slots_google_cache[
            "expires_at"
        ]
    ):
        return _ats_copy_busy_intervals(
            cached
        )

    with _city_slots_google_cache_lock:

        now = time.monotonic()

        cached = (
            _city_slots_google_cache[
                "busy_intervals"
            ]
        )

        if (
            cached is not None
            and now
            < _city_slots_google_cache[
                "expires_at"
            ]
        ):
            return _ats_copy_busy_intervals(
                cached
            )

        try:
            busy_intervals = (
                get_busy_intervals_from_google()
            )

        except Exception:

            if cached is not None:
                return _ats_copy_busy_intervals(
                    cached
                )

            raise

        _city_slots_google_cache[
            "busy_intervals"
        ] = _ats_copy_busy_intervals(
            busy_intervals
        )

        _city_slots_google_cache[
            "expires_at"
        ] = (
            time.monotonic()
            + _CITY_SLOTS_GOOGLE_CACHE_TTL
        )

        return _ats_copy_busy_intervals(
            busy_intervals
        )


def _ats_available_windows(
    day,
    busy_intervals,
    local_now
):
    start_minute = (
        _STUDIO_START_MINUTE
    )

    end_minute = (
        _STUDIO_END_MINUTE
    )

    # Сегодня нельзя предлагать уже
    # прошедшую часть рабочего дня.
    if day < local_now.date():
        return []

    if day == local_now.date():

        current_minute = (
            local_now.hour * 60
            + local_now.minute
        )

        if (
            local_now.second
            or local_now.microsecond
        ):
            current_minute += 1

        start_minute = max(
            start_minute,
            current_minute
        )

    if start_minute >= end_minute:
        return []

    merged_busy = _ats_merge_intervals(
        busy_intervals.get(
            day.isoformat(),
            []
        )
    )

    windows = []
    cursor = start_minute

    for busy_start, busy_end in merged_busy:

        if busy_end <= cursor:
            continue

        if busy_start >= end_minute:
            break

        if busy_start > cursor:
            windows.append(
                (
                    cursor,
                    min(
                        busy_start,
                        end_minute
                    )
                )
            )

        cursor = max(
            cursor,
            busy_end
        )

        if cursor >= end_minute:
            break

    if cursor < end_minute:
        windows.append(
            (
                cursor,
                end_minute
            )
        )

    return [
        (start, end)
        for start, end in windows
        if end > start
    ]


def _ats_windows_payload(windows):
    return [
        {
            "start": _ats_minutes_label(
                start
            ),
            "end": _ats_minutes_label(
                end
            )
        }
        for start, end in windows
    ]


def _ats_windows_label(windows):
    if not windows:
        return ""

    if len(windows) == 1:

        start, end = windows[0]

        if (
            start == _STUDIO_START_MINUTE
            and end == _STUDIO_END_MINUTE
        ):
            return "10:00–23:00"

        if (
            start == _STUDIO_START_MINUTE
            and end < _STUDIO_END_MINUTE
        ):
            return (
                "до "
                + _ats_minutes_label(end)
            )

        if (
            start > _STUDIO_START_MINUTE
            and end == _STUDIO_END_MINUTE
        ):
            return (
                "после "
                + _ats_minutes_label(start)
            )

        return (
            _ats_minutes_label(start)
            + "–"
            + _ats_minutes_label(end)
        )

    return " / ".join(
        (
            _ats_minutes_label(start)
            + "–"
            + _ats_minutes_label(end)
        )
        for start, end in windows
    )


# === END GOOGLE CALENDAR SYNC ===



@app.get("/api/city-slots")
def api_city_slots():

    busy_intervals = (
        get_busy_intervals_from_google_cached()
    )

    local_now = (
        datetime
        .now(timezone.utc)
        .astimezone(_SPB_PUBLIC_TZ)
    )

    today = local_now.date()

    connection = get_db_connection()

    cursor = connection.cursor(
        cursor_factory=
            psycopg2.extras.RealDictCursor
    )

    cursor.execute("""
        SELECT
            id,
            city,
            date_label,
            slot_date,
            slot_time,
            status,
            note
        FROM city_slots
        WHERE status IN (
            'available',
            'booked'
        )
        ORDER BY
            slot_date ASC NULLS LAST;
    """)

    manual_slots = cursor.fetchall()

    cursor.close()
    connection.close()

    result = {
        "spb": [],
        "smolensk": [],
        "moscow": []
    }


    # ------------------------------
    # Ручные записи из админки
    # ------------------------------

    for row in manual_slots:

        city = row["city"]

        if city not in result:
            continue

        slot_date = row[
            "slot_date"
        ]

        if (
            slot_date
            and slot_date < today
        ):
            continue

        status_value = row[
            "status"
        ]

        # Москва / Смоленск пока
        # остаются как раньше.
        if (
            city != "spb"
            or not slot_date
        ):
            result[city].append({
                "id": row["id"],
                "city": city,
                "date_label":
                    row["date_label"],
                "slot_date": (
                    slot_date.isoformat()
                    if slot_date
                    else None
                ),
                "slot_time":
                    row["slot_time"],
                "status":
                    status_value
            })

            continue

        # Ручной booked должен
        # продолжать блокировать дату.
        if status_value == "booked":

            result["spb"].append({
                "id": row["id"],
                "city": "spb",
                "date_label":
                    row["date_label"],
                "slot_date":
                    slot_date.isoformat(),
                "slot_time":
                    row["slot_time"],
                "status": "booked",
                "available_windows": []
            })

            continue

        windows = _ats_available_windows(
            slot_date,
            busy_intervals,
            local_now
        )

        if not windows:
            continue

        result["spb"].append({
            "id": row["id"],
            "city": "spb",
            "date_label":
                row["date_label"],
            "slot_date":
                slot_date.isoformat(),
            "slot_time":
                _ats_windows_label(
                    windows
                ),
            "status": "available",
            "available_windows":
                _ats_windows_payload(
                    windows
                )
        })


    # ------------------------------
    # Автоматические даты СПб
    # ------------------------------

    first_month = today.replace(
        day=1
    )

    first_after_next_month = (
        first_month
        + timedelta(days=70)
    ).replace(
        day=1
    )

    last_next_month = (
        first_after_next_month
        - timedelta(days=1)
    )

    total_days = (
        last_next_month
        - today
    ).days + 1

    for i in range(total_days):

        day = (
            today
            + timedelta(days=i)
        )

        day_str = day.isoformat()

        exists = any(
            item.get("slot_date")
            == day_str
            for item
            in result["spb"]
        )

        if exists:
            continue

        windows = _ats_available_windows(
            day,
            busy_intervals,
            local_now
        )

        if not windows:
            continue

        result["spb"].append({
            "id": None,
            "city": "spb",
            "date_label":
                day.strftime(
                    "%d.%m.%Y"
                ),
            "slot_date":
                day_str,
            "slot_time":
                _ats_windows_label(
                    windows
                ),
            "status":
                "available",
            "available_windows":
                _ats_windows_payload(
                    windows
                )
        })


    result["spb"] = sorted(
        result["spb"],
        key=lambda item:
            item.get("slot_date")
            or "9999"
    )

    return result


# === /city slots api ===


# === city slots admin ===

@app.get("/admin/city-slots", response_class=HTMLResponse)
async def admin_city_slots(request: Request, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT
            id,
            city,
            date_label,
            slot_date,
            slot_time,
            status,
            note,
            sort_order,
            created_at,
            updated_at
        FROM city_slots
        ORDER BY
            city,
            sort_order ASC,
            slot_date ASC NULLS LAST,
            id ASC;
    """)

    slots = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_city_slots.html",
        context={
            "title": "Свободные даты",
            "slots": slots
        }
    )


@app.post("/admin/city-slots")
async def admin_city_slot_create(
    city: str = Form(...),
    date_label: str = Form(...),
    slot_date: str = Form(""),
    slot_time: str = Form(""),
    status_value: str = Form("available"),
    note: str = Form(""),
    sort_order: int = Form(100),
    admin: str = Depends(verify_admin)
):
    if city not in {"spb", "smolensk", "moscow"}:
        raise HTTPException(status_code=400, detail="Недопустимый город")

    if status_value not in {"available", "hidden", "booked"}:
        raise HTTPException(status_code=400, detail="Недопустимый статус")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO city_slots (
            city,
            date_label,
            slot_date,
            slot_time,
            status,
            note,
            sort_order,
            updated_at
        )
        VALUES (%s, %s, NULLIF(%s, '')::date, NULLIF(%s, ''), %s, NULLIF(%s, ''), %s, CURRENT_TIMESTAMP);
    """, (
        city,
        date_label.strip(),
        slot_date.strip(),
        slot_time.strip(),
        status_value,
        note.strip(),
        sort_order
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/city-slots",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.post("/admin/city-slots/{slot_id}/edit")
async def admin_city_slot_edit(
    slot_id: int,
    city: str = Form(...),
    date_label: str = Form(...),
    slot_date: str = Form(""),
    slot_time: str = Form(""),
    status_value: str = Form("available"),
    note: str = Form(""),
    sort_order: int = Form(100),
    admin: str = Depends(verify_admin)
):
    if city not in {"spb", "smolensk", "moscow"}:
        raise HTTPException(status_code=400, detail="Недопустимый город")

    if status_value not in {"available", "hidden", "booked"}:
        raise HTTPException(status_code=400, detail="Недопустимый статус")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE city_slots
        SET
            city = %s,
            date_label = %s,
            slot_date = NULLIF(%s, '')::date,
            slot_time = NULLIF(%s, ''),
            status = %s,
            note = NULLIF(%s, ''),
            sort_order = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    """, (
        city,
        date_label.strip(),
        slot_date.strip(),
        slot_time.strip(),
        status_value,
        note.strip(),
        sort_order,
        slot_id
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/city-slots",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.post("/admin/city-slots/{slot_id}/delete")
async def admin_city_slot_delete(
    slot_id: int,
    admin: str = Depends(verify_admin)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM city_slots WHERE id = %s;", (slot_id,))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/city-slots",
        status_code=status.HTTP_303_SEE_OTHER
    )

# === /city slots admin ===


# === project media api ===


# Home page carousel media block key
CAROUSEL_BLOCK_KEY = "home_carousel"

@app.get("/admin/carousel", response_class=HTMLResponse)
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


@app.post("/admin/carousel/media/upload")
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


@app.post("/admin/carousel/media/{media_id}/edit")
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


@app.post("/admin/carousel/media/{media_id}/toggle")
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


@app.post("/admin/carousel/media/{media_id}/delete")
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

@app.get("/api/home-carousel")
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


@app.post("/admin/carousel/cards/{target_key}/edit")
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
@app.post("/admin/carousel/certificate-settings")
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

@app.get("/api/category-media/{slug}")
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

# === /category media api ===


# === upload check admin page ===

@app.get("/admin/upload-check", response_class=HTMLResponse)
async def admin_upload_check(
    request: Request,
    admin: str = Depends(verify_admin)
):
    return templates.TemplateResponse(
        request=request,
        name="admin_upload_check.html",
        context={
            "title": "Проверка загрузок"
        }
    )

# === /upload check admin page ===


# === registered extracted routes ===
from app.routes_health import register_health_routes

register_health_routes(app, get_db_connection)

from app.routes_legal import register_legal_routes

register_legal_routes(app, templates, get_db_connection, verify_admin)

from app.routes_auth import register_auth_routes

register_auth_routes(app, templates)


from app.routes_media import register_media_routes

register_media_routes(app, templates, get_db_connection, verify_admin)


from app.routes_project_media import register_project_media_routes

register_project_media_routes(app, get_db_connection, verify_admin)

# === /registered extracted routes ===

# === RESTORED_ADMIN_SYSTEM_ROUTE_V2 ===
try:
    from app.routes_admin_system import register_admin_system_routes

    if not any(
        getattr(route, "path", "") == "/admin/system"
        for route in app.routes
    ):
        register_admin_system_routes(
            app,
            templates,
            verify_admin,
        )
except Exception:
    import logging
    logging.exception(
        "Failed to register admin system routes"
    )
# === /RESTORED_ADMIN_SYSTEM_ROUTE_V2 ===


# Local site statistics
from app.routes_stats import register_stats_routes

register_stats_routes(app, templates, get_db_connection, verify_admin)

# ATS_CLIENT_CABINET_SAFE_IMPORT_START
try:
    from app.routes_client_cabinet import register_client_cabinet_routes
    CLIENT_CABINET_IMPORT_ERROR = None
except Exception as exc:
    CLIENT_CABINET_IMPORT_ERROR = exc

    def register_client_cabinet_routes(*args, **kwargs):
        return None
# ATS_CLIENT_CABINET_SAFE_IMPORT_END


# ATS_CLIENT_CABINET_SAFE_REGISTER_START
try:
    register_client_cabinet_routes(app, templates, get_db_connection, verify_admin)
    CLIENT_CABINET_REGISTER_ERROR = None
except Exception as exc:
    CLIENT_CABINET_REGISTER_ERROR = exc
# ATS_CLIENT_CABINET_SAFE_REGISTER_END

from app.routes_leads_simple_crm import register_simple_leads_crm_routes

register_simple_leads_crm_routes(app, templates, get_db_connection, verify_admin)


# ATS_ANNOUNCEMENT_SAFE_IMPORT_START
try:
    from app.routes_announcement import register_announcement_routes
    ANNOUNCEMENT_IMPORT_ERROR = None
except Exception as exc:
    register_announcement_routes = None
    ANNOUNCEMENT_IMPORT_ERROR = repr(exc)
# ATS_ANNOUNCEMENT_SAFE_IMPORT_END

# ATS_ANNOUNCEMENT_SAFE_REGISTER_START
ANNOUNCEMENT_REGISTER_ERROR = None
try:
    if register_announcement_routes:
        register_announcement_routes(app, templates, get_db_connection, verify_admin)
except Exception as exc:
    ANNOUNCEMENT_REGISTER_ERROR = repr(exc)
# ATS_ANNOUNCEMENT_SAFE_REGISTER_END


# ATS_CLEAN_STATS_SAFE_IMPORT_START
try:
    from app.routes_clean_stats import register_clean_stats_routes
    CLEAN_STATS_IMPORT_ERROR = None
except Exception as exc:
    register_clean_stats_routes = None
    CLEAN_STATS_IMPORT_ERROR = repr(exc)
# ATS_CLEAN_STATS_SAFE_IMPORT_END

# ATS_CLEAN_STATS_SAFE_REGISTER_START
CLEAN_STATS_REGISTER_ERROR = None
try:
    if register_clean_stats_routes:
        register_clean_stats_routes(app, get_db_connection, verify_admin)
except Exception as exc:
    CLEAN_STATS_REGISTER_ERROR = repr(exc)
# ATS_CLEAN_STATS_SAFE_REGISTER_END
