import psycopg2
import psycopg2.extras
from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from app.auth import verify_admin
from app.db import get_db_connection
from app.views import templates
from fastapi import APIRouter

router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
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


@router.get("/admin/upload-check", response_class=HTMLResponse)
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
