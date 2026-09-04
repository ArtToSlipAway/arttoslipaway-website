import psycopg2.extras
from fastapi import Depends, Form, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse


DEFAULT_TEXT = (
    "Сайт активно наполняется работами и медиа. "
    "Разделы обновляются, свободные эскизы уже доступны, "
    "запись на татуировку открыта."
)


def _clamp(value, default=85, minimum=10, maximum=240):
    try:
        value = int(value)
    except Exception:
        value = default

    return max(minimum, min(maximum, value))


def _get_settings(get_db_connection):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS site_announcement (
            id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
            is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            text TEXT NOT NULL DEFAULT '',
            desktop_seconds INTEGER NOT NULL DEFAULT 85,
            mobile_seconds INTEGER NOT NULL DEFAULT 75,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """)

    cursor.execute("""
        INSERT INTO site_announcement (
            id,
            is_enabled,
            text,
            desktop_seconds,
            mobile_seconds
        )
        VALUES (1, TRUE, %s, 85, 75)
        ON CONFLICT (id) DO NOTHING;
    """, (DEFAULT_TEXT,))

    connection.commit()

    cursor.execute("""
        SELECT
            is_enabled,
            text,
            desktop_seconds,
            mobile_seconds,
            updated_at
        FROM site_announcement
        WHERE id = 1;
    """)

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        return {
            "is_enabled": True,
            "text": DEFAULT_TEXT,
            "desktop_seconds": 85,
            "mobile_seconds": 75,
            "updated_at": None,
        }

    return dict(row)


def register_announcement_routes(app, templates, get_db_connection, verify_admin):
    @app.get("/api/announcement")
    async def api_announcement():
        try:
            row = _get_settings(get_db_connection)
        except Exception:
            return JSONResponse({
                "enabled": False,
                "text": "",
                "desktop_seconds": 85,
                "mobile_seconds": 75,
            })

        return JSONResponse({
            "enabled": bool(row.get("is_enabled")),
            "text": str(row.get("text") or "").strip(),
            "desktop_seconds": _clamp(row.get("desktop_seconds"), 85, 10, 240),
            "mobile_seconds": _clamp(row.get("mobile_seconds"), 75, 10, 240),
        })

    @app.get("/admin/announcement", response_class=HTMLResponse)
    async def admin_announcement(
        request: Request,
        saved: int = 0,
        admin: str = Depends(verify_admin),
    ):
        row = _get_settings(get_db_connection)

        return templates.TemplateResponse(
            request=request,
            name="admin_announcement.html",
            context={
                "announcement": row,
                "saved": saved,
            },
        )

    @app.post("/admin/announcement")
    async def admin_announcement_save(
        is_enabled: str = Form("off"),
        text: str = Form(""),
        desktop_seconds: int = Form(85),
        mobile_seconds: int = Form(75),
        admin: str = Depends(verify_admin),
    ):
        clean_text = " ".join((text or "").split()).strip()

        if len(clean_text) > 420:
            clean_text = clean_text[:420]

        desktop = _clamp(desktop_seconds, 85, 10, 240)
        mobile = _clamp(mobile_seconds, 75, 10, 240)
        enabled = is_enabled == "on"

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO site_announcement (
                id,
                is_enabled,
                text,
                desktop_seconds,
                mobile_seconds,
                updated_at
            )
            VALUES (1, %s, %s, %s, %s, NOW())
            ON CONFLICT (id) DO UPDATE
            SET
                is_enabled = EXCLUDED.is_enabled,
                text = EXCLUDED.text,
                desktop_seconds = EXCLUDED.desktop_seconds,
                mobile_seconds = EXCLUDED.mobile_seconds,
                updated_at = NOW();
        """, (enabled, clean_text, desktop, mobile))

        connection.commit()
        cursor.close()
        connection.close()

        return RedirectResponse(
            url="/admin/announcement?saved=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )
