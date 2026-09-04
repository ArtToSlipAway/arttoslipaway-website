from typing import List, Optional
import psycopg2
import psycopg2.extras
from fastapi import Request, Form, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.upload_core import REFERENCE_UPLOAD_EXTENSIONS, save_upload_file
from app.paths import PRIVATE_UPLOADS_DIR
from app.db import get_db_connection
from app.views import templates
from app.certificates import CERTIFICATE_SETTINGS_DEFAULTS, get_certificate_settings, get_certificate_min_nominal
from fastapi import APIRouter

router = APIRouter()

@router.get("/request", response_class=HTMLResponse)
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


@router.post("/request")
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
    if len(reference_files or []) > 4:
        raise HTTPException(status_code=400, detail="Не более четырёх вложений")

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

    created_files = []
    try:
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
                    private=True,
                )

                if file_path:
                    created_files.append(PRIVATE_UPLOADS_DIR / file_path.split("/", 1)[1])

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

    except Exception:
        connection.rollback()
        for path in created_files:
            path.unlink(missing_ok=True)
        raise
    finally:
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
