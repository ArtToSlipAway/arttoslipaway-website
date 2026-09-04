"""Application assembly. Business routes live in focused modules."""
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic
from fastapi.templating import Jinja2Templates
from app.paths import ENV_PATH, STATIC_DIR, TEMPLATES_DIR, UPLOADS_DIR

load_dotenv(ENV_PATH)
from app.auth import verify_admin
from app.db import get_db_connection

app = FastAPI(title="ArtToSlipAway")
security = HTTPBasic(auto_error=False)


@app.middleware("http")
async def private_response_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/admin", "/client/")):
        response.headers["Cache-Control"] = "no-store"
        # no-referrer on an HTML form can make browsers send Origin: null.
        # Admin forms need same-origin; bearer-token client pages must not leak URLs.
        response.headers.setdefault("Referrer-Policy",
            "no-referrer" if request.url.path.startswith("/client/") else "same-origin"
        )
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


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

from app.views import templates


from app.routes_public import router as routes_public_router
app.include_router(routes_public_router)

from app.routes_requests import router as routes_requests_router
app.include_router(routes_requests_router)

from app.routes_admin_projects import router as routes_admin_projects_router
app.include_router(routes_admin_projects_router)

from app.routes_admin_categories import router as routes_admin_categories_router
app.include_router(routes_admin_categories_router)

from app.routes_admin_visual import router as routes_admin_visual_router
app.include_router(routes_admin_visual_router)

from app.routes_admin_dashboard import router as routes_admin_dashboard_router
app.include_router(routes_admin_dashboard_router)

from app.routes_calendar import router as routes_calendar_router
app.include_router(routes_calendar_router)

from app.routes_carousel import router as routes_carousel_router
app.include_router(routes_carousel_router)

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

from app.routes_admin_system import register_admin_system_routes
register_admin_system_routes(app, templates, verify_admin)

from app.routes_stats import register_stats_routes
register_stats_routes(app, templates, get_db_connection, verify_admin)

from app.routes_client_cabinet import register_client_cabinet_routes
register_client_cabinet_routes(app, templates, get_db_connection, verify_admin)

from app.routes_leads_simple_crm import register_simple_leads_crm_routes
register_simple_leads_crm_routes(app, templates, get_db_connection, verify_admin)

from app.routes_announcement import register_announcement_routes
register_announcement_routes(app, templates, get_db_connection, verify_admin)

from app.routes_clean_stats import register_clean_stats_routes
register_clean_stats_routes(app, get_db_connection, verify_admin)

from app.routes_private_files import register_private_file_routes
register_private_file_routes(app, get_db_connection, verify_admin)
