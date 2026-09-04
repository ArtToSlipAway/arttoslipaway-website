import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Optional
from urllib.parse import quote

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic(auto_error=False)

ADMIN_COOKIE_NAME = "ats_admin_session"
ADMIN_SESSION_TTL_SECONDS = 60 * 60 * 24 * 7


def get_admin_login() -> str:
    return (
        os.getenv("ADMIN_LOGIN")
        or os.getenv("ADMIN_USERNAME")
        or "admin"
    )


def get_admin_password() -> str:
    return (
        os.getenv("ADMIN_PASSWORD")
        or os.getenv("ADMIN_PASS")
        or ""
    )


def get_admin_session_secret() -> str:
    secret = os.getenv("ADMIN_SESSION_SECRET", "").strip()
    if not secret:
        raise RuntimeError("ADMIN_SESSION_SECRET must be configured")
    return secret


def is_secure_admin_cookie() -> bool:
    return (os.getenv("ADMIN_COOKIE_SECURE") or "false").lower() == "true"


def sign_admin_payload(payload: str) -> str:
    signature = hmac.new(
        get_admin_session_secret().encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")


def make_admin_token(username: str) -> str:
    expires_at = int(time.time()) + ADMIN_SESSION_TTL_SECONDS
    raw_payload = f"{username}|{expires_at}|{secrets.token_urlsafe(16)}"

    payload = base64.urlsafe_b64encode(
        raw_payload.encode("utf-8")
    ).decode("utf-8").rstrip("=")

    signature = sign_admin_payload(payload)

    return f"{payload}.{signature}"


def verify_admin_token(token: str) -> Optional[str]:
    if not token or "." not in token:
        return None

    payload, signature = token.rsplit(".", 1)
    expected_signature = sign_admin_payload(payload)

    if not secrets.compare_digest(signature, expected_signature):
        return None

    try:
        padding = "=" * (-len(payload) % 4)
        raw_payload = base64.urlsafe_b64decode(payload + padding).decode("utf-8")
        username, expires_at_raw, _nonce = raw_payload.split("|", 2)
        expires_at = int(expires_at_raw)
    except Exception:
        return None

    if expires_at < int(time.time()):
        return None

    if username != get_admin_login():
        return None

    return username


def admin_login_redirect(request: Request):
    current_path = request.url.path

    if request.url.query:
        current_path = current_path + "?" + request.url.query

    next_url = quote(current_path, safe="")

    raise HTTPException(
        status_code=status.HTTP_303_SEE_OTHER,
        headers={
            "Location": f"/admin/login?next={next_url}"
        }
    )


async def verify_admin(
    request: Request,
    credentials: Optional[HTTPBasicCredentials] = Depends(security)
) -> str:
    token = request.cookies.get(ADMIN_COOKIE_NAME)
    session_user = verify_admin_token(token)

    if session_user:
        return session_user

    # Резервный вход через Basic Auth оставлен на переходный период.
    if credentials and get_admin_password():
        correct_username = secrets.compare_digest(
            credentials.username.encode("utf-8"),
            get_admin_login().encode("utf-8")
        )
        correct_password = secrets.compare_digest(
            credentials.password.encode("utf-8"),
            get_admin_password().encode("utf-8")
        )

        if correct_username and correct_password:
            return credentials.username

    admin_login_redirect(request)
