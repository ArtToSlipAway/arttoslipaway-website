import hashlib
import asyncio
from functools import partial
import os
import time
from urllib.parse import urlparse

import psycopg2.extras
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from starlette.background import BackgroundTask, BackgroundTasks


IGNORED_PREFIXES = (
    "/client/",  # Bearer tokens must never enter analytics records.
    "/health",
    "/admin",
    "/static",
    "/uploads",
    "/api/admin",
    "/api/",
)

IGNORED_EXACT_PATHS = (
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
)

IGNORED_EXTENSIONS = (
    ".css", ".js", ".map",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico",
    ".mp4", ".mov", ".webm", ".mp3", ".wav",
    ".woff", ".woff2", ".ttf", ".otf",
)


def should_track_request(request: Request) -> bool:
    path = request.url.path

    if request.method not in ("GET", "HEAD"):
        return False

    if path in IGNORED_EXACT_PATHS:
        return False

    if path.startswith(IGNORED_PREFIXES):
        return False

    lower_path = path.lower()
    if lower_path.endswith(IGNORED_EXTENSIONS):
        return False

    return True


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for") or ""
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip") or ""
    if real_ip:
        return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return ""


def hash_ip(ip: str) -> str:
    if not ip:
        return None

    secret = os.getenv("STATS_IP_HASH_SECRET", "").strip()
    if not secret:
        raise RuntimeError("STATS_IP_HASH_SECRET must be configured")

    return hashlib.sha256(f"{secret}|{ip}".encode("utf-8")).hexdigest()


def normalize_referer(request: Request) -> str:
    referer = request.headers.get("referer") or ""
    if not referer:
        return "direct"

    try:
        parsed = urlparse(referer)
        host = (parsed.netloc or "").lower()

        if not host:
            return "direct"

        if host in ("arttoslipaway.art", "www.arttoslipaway.art"):
            return "internal"

        return host[:255]
    except Exception:
        return "unknown"


def detect_device(user_agent: str) -> str:
    ua = (user_agent or "").lower()

    if "bot" in ua or "crawler" in ua or "spider" in ua:
        return "bot"

    if "ipad" in ua or "tablet" in ua:
        return "tablet"

    if "mobile" in ua or "iphone" in ua or "android" in ua:
        return "mobile"

    return "desktop"


def detect_browser(user_agent: str) -> str:
    ua = (user_agent or "").lower()

    if "edg/" in ua:
        return "Edge"
    if "opr/" in ua or "opera" in ua:
        return "Opera"
    if "chrome/" in ua and "chromium" not in ua:
        return "Chrome"
    if "safari/" in ua and "chrome/" not in ua:
        return "Safari"
    if "firefox/" in ua:
        return "Firefox"
    if "curl/" in ua:
        return "curl"
    if "bot" in ua or "crawler" in ua or "spider" in ua:
        return "Bot"

    return "Other"


def detect_bot(user_agent: str) -> bool:
    ua = (user_agent or "").lower()

    bot_markers = (
        "bot",
        "crawler",
        "spider",
        "slurp",
        "bingpreview",
        "yandex",
        "googlebot",
        "duckduckbot",
        "semrush",
        "ahrefs",
        "mj12bot",
        "curl/",
        "python-requests",
    )

    return any(marker in ua for marker in bot_markers)


def record_visit(get_db_connection, request: Request, status_code: int, response_time_ms: int):
    connection = None
    cursor = None

    try:
        user_agent = (request.headers.get("user-agent") or "")[:1000]
        device_type = detect_device(user_agent)
        browser = detect_browser(user_agent)
        is_bot = detect_bot(user_agent)

        ip = get_client_ip(request)
        ip_hash = hash_ip(ip)

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO site_visits (
                method,
                path,
                referer,
                user_agent,
                ip_hash,
                device_type,
                browser,
                status_code,
                response_time_ms,
                is_bot
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                request.method,
                request.url.path[:500],
                normalize_referer(request),
                user_agent,
                ip_hash,
                device_type,
                browser,
                status_code,
                response_time_ms,
                is_bot,
            )
        )

        connection.commit()
    except Exception as exc:
        print(f"[site_stats] record_visit failed: {exc}")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def attach_visit_recording(
    response,
    get_db_connection,
    request: Request,
    status_code: int,
    response_time_ms: int,
):
    task = BackgroundTask(
        record_visit,
        get_db_connection=get_db_connection,
        request=request,
        status_code=status_code,
        response_time_ms=response_time_ms,
    )

    if response.background is None:
        response.background = task
    else:
        response.background = BackgroundTasks([response.background, task])


def register_stats_routes(app, templates, get_db_connection, verify_admin):
    @app.middleware("http")
    async def site_stats_middleware(request: Request, call_next):
        should_track = should_track_request(request)
        started_at = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            if should_track:
                response_time_ms = int((time.perf_counter() - started_at) * 1000)
                asyncio.get_running_loop().run_in_executor(
                    None,
                    partial(
                        record_visit,
                        get_db_connection=get_db_connection,
                        request=request,
                        status_code=500,
                        response_time_ms=response_time_ms,
                    ),
                )
            raise

        if should_track:
            response_time_ms = int((time.perf_counter() - started_at) * 1000)
            attach_visit_recording(
                response=response,
                get_db_connection=get_db_connection,
                request=request,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
            )

        return response

    @app.get("/admin/stats", response_class=HTMLResponse)
    async def admin_stats_page(
        request: Request,
        admin_user: str = Depends(verify_admin)
    ):
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT
                COUNT(*) FILTER (
                    WHERE created_at >= date_trunc('day', now())
                      AND is_bot = FALSE
                ) AS visits_today,

                COUNT(*) FILTER (
                    WHERE created_at >= now() - interval '7 days'
                      AND is_bot = FALSE
                ) AS visits_7d,

                COUNT(*) FILTER (
                    WHERE created_at >= now() - interval '7 days'
                      AND path = '/request'
                      AND is_bot = FALSE
                ) AS request_views_7d,

                COUNT(*) FILTER (
                    WHERE created_at >= now() - interval '7 days'
                      AND (
                        path = '/projects'
                        OR path LIKE '/projects/%'
                        OR path LIKE '/categories/%'
                      )
                      AND is_bot = FALSE
                ) AS project_views_7d,

                COUNT(*) FILTER (
                    WHERE created_at >= now() - interval '7 days'
                      AND is_bot = TRUE
                ) AS bot_hits_7d
            FROM site_visits;
        """)
        summary = cursor.fetchone()

        cursor.execute("""
            SELECT path, COUNT(*) AS views
            FROM site_visits
            WHERE created_at >= now() - interval '7 days'
              AND is_bot = FALSE
            GROUP BY path
            ORDER BY views DESC, path
            LIMIT 20;
        """)
        top_pages = cursor.fetchall()

        cursor.execute("""
            SELECT referer, COUNT(*) AS visits
            FROM site_visits
            WHERE created_at >= now() - interval '7 days'
              AND is_bot = FALSE
            GROUP BY referer
            ORDER BY visits DESC, referer
            LIMIT 20;
        """)
        sources = cursor.fetchall()

        cursor.execute("""
            SELECT device_type, COUNT(*) AS visits
            FROM site_visits
            WHERE created_at >= now() - interval '7 days'
              AND is_bot = FALSE
            GROUP BY device_type
            ORDER BY visits DESC, device_type;
        """)
        devices = cursor.fetchall()

        cursor.execute("""
            SELECT browser, COUNT(*) AS visits
            FROM site_visits
            WHERE created_at >= now() - interval '7 days'
              AND is_bot = FALSE
            GROUP BY browser
            ORDER BY visits DESC, browser;
        """)
        browsers = cursor.fetchall()

        cursor.execute("""
            SELECT
                created_at,
                method,
                path,
                referer,
                device_type,
                browser,
                status_code,
                response_time_ms,
                is_bot
            FROM site_visits
            ORDER BY created_at DESC
            LIMIT 50;
        """)
        recent_visits = cursor.fetchall()

        cursor.close()
        connection.close()

        return templates.TemplateResponse(
            request=request,
            name="admin_stats.html",
            context={
                "title": "Статистика сайта",
                "admin_user": admin_user,
                "summary": summary,
                "top_pages": top_pages,
                "sources": sources,
                "devices": devices,
                "browsers": browsers,
                "recent_visits": recent_visits,
            }
        )
