import secrets
from typing import Optional

from fastapi import Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import (
    ADMIN_COOKIE_NAME,
    ADMIN_SESSION_TTL_SECONDS,
    get_admin_login,
    get_admin_password,
    is_secure_admin_cookie,
    make_admin_token,
    verify_admin_token,
)


def safe_admin_redirect(value: Optional[str]) -> str:
    """Keep login redirects inside the administrative area."""
    value = value or "/admin"
    if any(character in value for character in ("\\", "\r", "\n")):
        return "/admin"
    if value == "/admin" or value.startswith(("/admin/", "/admin?")):
        return value
    return "/admin"


def register_auth_routes(app, templates):
    @app.get("/admin/login", response_class=HTMLResponse)
    async def admin_login_page(
        request: Request,
        next_url_query: Optional[str] = Query("/admin", alias="next")
    ):
        token = request.cookies.get(ADMIN_COOKIE_NAME)

        if verify_admin_token(token):
            return RedirectResponse(
                url=safe_admin_redirect(next_url_query),
                status_code=status.HTTP_303_SEE_OTHER
            )

        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={
                "title": "Вход в админку",
                "next_url": next_url_query or "/admin",
                "error": ""
            }
        )


    @app.post("/admin/login", response_class=HTMLResponse)
    async def admin_login_submit(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        next_url: str = Form("/admin")
    ):
        correct_username = secrets.compare_digest(
            username.encode("utf-8"),
            get_admin_login().encode("utf-8"),
        )
        correct_password = secrets.compare_digest(
            password.encode("utf-8"),
            get_admin_password().encode("utf-8"),
        )

        if not get_admin_password() or not correct_username or not correct_password:
            return templates.TemplateResponse(
                request=request,
                name="admin_login.html",
                status_code=401,
                context={
                    "title": "Вход в админку",
                    "next_url": next_url or "/admin",
                    "error": "Неверный логин или пароль"
                }
            )

        next_url = safe_admin_redirect(next_url)

        response = RedirectResponse(
            url=next_url,
            status_code=status.HTTP_303_SEE_OTHER
        )

        response.set_cookie(
            key=ADMIN_COOKIE_NAME,
            value=make_admin_token(username),
            max_age=ADMIN_SESSION_TTL_SECONDS,
            httponly=True,
            secure=is_secure_admin_cookie(),
            samesite="lax",
            path="/admin"
        )

        return response
    @app.get("/admin/logout")
    async def admin_logout():
        response = RedirectResponse(
            url="/admin/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

        response.delete_cookie(
            key=ADMIN_COOKIE_NAME,
            path="/admin"
        )

        return response
