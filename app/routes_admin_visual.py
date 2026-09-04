from typing import Optional
import psycopg2
import psycopg2.extras
from fastapi import Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.upload_core import save_upload_file
from app.auth import verify_admin
from app.db import get_db_connection
from app.views import templates
from fastapi import APIRouter

router = APIRouter()

@router.get("/admin/visual", response_class=HTMLResponse)
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


@router.post("/admin/visual")
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
