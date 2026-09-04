import psycopg2.extras
from fastapi import Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse


VALID_VIEWS = {"active", "archived", "trash"}

STATUS_LABELS = {
    "new": "Новая",
    "in_work": "В работе",
    "waiting": "Ждёт ответа",
    "done": "Завершена",
    "declined": "Declined",
    "rejected": "Отклонена",
}

VALID_STATUSES = set(STATUS_LABELS.keys())


def _redirect_to_view(view: str = "active"):
    if view not in VALID_VIEWS:
        view = "active"
    return RedirectResponse(
        url=f"/admin/leads?view={view}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


def register_simple_leads_crm_routes(app, templates, get_db_connection, verify_admin):
    @app.get("/admin/leads", response_class=HTMLResponse)
    async def admin_leads_crm(
        request: Request,
        view: str = Query("active"),
        admin: str = Depends(verify_admin),
    ):
        if view not in VALID_VIEWS:
            view = "active"

        where_by_view = {
            "active": "l.archived_at IS NULL AND l.trashed_at IS NULL",
            "archived": "l.archived_at IS NOT NULL AND l.trashed_at IS NULL",
            "trash": "l.trashed_at IS NOT NULL",
        }

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT
                COUNT(*) FILTER (WHERE archived_at IS NULL AND trashed_at IS NULL) AS active_count,
                COUNT(*) FILTER (WHERE archived_at IS NOT NULL AND trashed_at IS NULL) AS archived_count,
                COUNT(*) FILTER (WHERE trashed_at IS NOT NULL) AS trash_count
            FROM leads;
        """)
        counts = cursor.fetchone()

        cursor.execute(f"""
            SELECT
                l.*,
                COALESCE(
                    (
                        SELECT json_agg(
                            json_build_object(
                                'id', lf.id,
                                'file_path', lf.file_path,
                                'original_filename', lf.original_filename,
                                'file_type', lf.file_type
                            )
                            ORDER BY lf.id ASC
                        )
                        FROM lead_files lf
                        WHERE lf.lead_id = l.id
                    ),
                    '[]'::json
                ) AS files
            FROM leads l
            WHERE {where_by_view[view]}
            ORDER BY l.created_at DESC, l.id DESC;
        """)

        leads = cursor.fetchall()

        cursor.close()
        connection.close()

        return templates.TemplateResponse(
            request=request,
            name="admin_leads.html",
            context={
                "leads": leads,
                "view": view,
                "counts": counts,
                "status_labels": STATUS_LABELS,
            },
        )

    @app.post("/admin/leads/{lead_id}/status")
    async def admin_lead_status_crm(
        lead_id: int,
        lead_status: str = Form(...),
        view: str = Form("active"),
        admin: str = Depends(verify_admin),
    ):
        if lead_status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Недопустимый статус заявки")

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE leads
            SET lead_status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (lead_status, lead_id))
        connection.commit()
        cursor.close()
        connection.close()

        return _redirect_to_view(view)

    @app.post("/admin/leads/{lead_id}/note")
    async def admin_lead_note_crm(
        lead_id: int,
        master_note: str = Form(""),
        view: str = Form("active"),
        admin: str = Depends(verify_admin),
    ):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE leads
            SET master_note = NULLIF(%s, ''),
                admin_note = NULLIF(%s, ''),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (master_note.strip(), master_note.strip(), lead_id))
        connection.commit()
        cursor.close()
        connection.close()

        return _redirect_to_view(view)

    @app.post("/admin/leads/{lead_id}/action")
    async def admin_lead_action_crm(
        lead_id: int,
        action: str = Form(...),
        view: str = Form("active"),
        admin: str = Depends(verify_admin),
    ):
        connection = get_db_connection()
        cursor = connection.cursor()

        if action == "archive":
            cursor.execute("""
                UPDATE leads
                SET archived_at = NOW(),
                    trashed_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """, (lead_id,))
            target_view = "active"

        elif action == "trash":
            cursor.execute("""
                UPDATE leads
                SET trashed_at = NOW(),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """, (lead_id,))
            target_view = "active" if view != "archived" else "archived"

        elif action == "restore":
            cursor.execute("""
                UPDATE leads
                SET archived_at = NULL,
                    trashed_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """, (lead_id,))
            target_view = "active"

        elif action == "delete":
            cursor.execute("DELETE FROM leads WHERE id = %s;", (lead_id,))
            target_view = "trash"

        else:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=400, detail="Недопустимое действие")

        connection.commit()
        cursor.close()
        connection.close()

        return _redirect_to_view(target_view)
