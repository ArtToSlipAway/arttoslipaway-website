from typing import Optional
import psycopg2
import psycopg2.extras
from fastapi import Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.upload_core import save_upload_file
from app.auth import verify_admin
from app.db import get_db_connection
from app.views import templates
from fastapi import APIRouter

router = APIRouter()

@router.get("/admin/projects", response_class=HTMLResponse)
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


@router.get("/admin/projects/new", response_class=HTMLResponse)
async def admin_project_new(request: Request, admin: str = Depends(verify_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin_project_new.html",
        context={"title": "Добавить проект"}
    )


@router.post("/admin/projects/new")
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


@router.get("/admin/projects/{project_id}/edit", response_class=HTMLResponse)
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


@router.post("/admin/projects/{project_id}/edit")
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


@router.post("/admin/projects/{project_id}/category")
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


@router.post("/admin/projects/{project_id}/order")
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


@router.post("/admin/projects/{project_id}/hide")
async def admin_project_hide(project_id: int, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE projects SET status = 'hidden' WHERE id = %s;", (project_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.post("/admin/projects/{project_id}/restore")
async def admin_project_restore(project_id: int, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE projects SET status = 'available' WHERE id = %s;", (project_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.post("/admin/projects/{project_id}/delete")
async def admin_project_delete(project_id: int, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM projects WHERE id = %s;", (project_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return RedirectResponse(url="/admin/projects", status_code=303)
