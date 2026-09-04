import psycopg2.extras
from fastapi import Depends
from fastapi.responses import JSONResponse


BOT_UA_RE = (
    r"(bot|crawler|spider|slurp|curl|wget|python|httpx|aiohttp|okhttp|"
    r"go-http-client|headless|lighthouse|wordpress|zgrab|masscan|nmap|sqlmap|"
    r"semrush|ahrefs|bingbot|googlebot|yandexbot|facebookexternalhit)"
)


def _qi(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def _columns(connection, table_name):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s;
        """,
        (table_name,),
    )
    cols = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return cols


def _first(cols, names):
    for name in names:
        if name in cols:
            return name
    return None


def _count(cursor, where_sql, params):
    cursor.execute(
        f"SELECT COUNT(*) AS count FROM site_visits WHERE {where_sql};",
        params,
    )
    return int(cursor.fetchone()["count"] or 0)


def _rows(cursor, label_sql, where_sql, params, limit=12):
    cursor.execute(
        f"""
        SELECT
            {label_sql} AS label,
            COUNT(*) AS count
        FROM site_visits
        WHERE {where_sql}
        GROUP BY 1
        ORDER BY count DESC
        LIMIT %s;
        """,
        [*params, limit],
    )

    return [
        {
            "label": str(row["label"] or "—"),
            "count": int(row["count"] or 0),
        }
        for row in cursor.fetchall()
    ]


def _build_filters(cols, days=7, today=False):
    time_col = _first(cols, ["created_at", "visited_at", "timestamp", "visit_time", "time"])
    path_col = _first(cols, ["path", "url_path", "page_path", "page", "request_path"])
    method_col = _first(cols, ["method", "request_method"])
    status_col = _first(cols, ["status_code", "status"])
    ua_col = _first(cols, ["user_agent", "ua"])
    source_col = _first(cols, ["source", "referrer_source", "referrer", "referer"])
    is_bot_col = _first(cols, ["is_bot", "bot"])

    conditions = []
    params = []

    if time_col:
        if today:
            conditions.append(f"{_qi(time_col)}::date = CURRENT_DATE")
        else:
            conditions.append(f"{_qi(time_col)} >= NOW() - INTERVAL '{int(days)} days'")

    if method_col:
        conditions.append(f"UPPER(COALESCE({_qi(method_col)}::text, 'GET')) = 'GET'")

    if status_col:
        conditions.append(f"COALESCE({_qi(status_col)}::int, 200) BETWEEN 200 AND 399")

    if path_col:
        p = f"LOWER(COALESCE({_qi(path_col)}::text, ''))"

        # Только публичные страницы, которые реально относятся к воронке.
        conditions.append(
            f"""(
                {p} = '/'
                OR {p} = '/request'
                OR {p} = '/projects'
                OR {p} = '/thanks'
                OR {p} LIKE '/categories/%%'
                OR {p} LIKE '/projects/%%'
                OR {p} LIKE '/project/%%'
            )"""
        )

        # Явно вырезаем технику и юридические страницы.
        conditions.append(
            f"""NOT (
                {p} LIKE '/admin%%'
                OR {p} LIKE '/api%%'
                OR {p} LIKE '/static%%'
                OR {p} LIKE '/uploads%%'
                OR {p} LIKE '/wp-%%'
                OR {p} LIKE '/xmlrpc%%'
                OR {p} LIKE '/phpmyadmin%%'
                OR {p} LIKE '/vendor%%'
                OR {p} LIKE '/.env%%'
                OR {p} LIKE '/.git%%'
                OR {p} IN ('/privacy', '/consent', '/terms', '/cookies', '/robots.txt', '/sitemap.xml', '/favicon.ico')
            )"""
        )

    if is_bot_col:
        conditions.append(f"COALESCE({_qi(is_bot_col)}, false) = false")

    if ua_col:
        conditions.append(f"COALESCE({_qi(ua_col)}::text, '') !~* %s")
        params.append(BOT_UA_RE)

    if source_col:
        conditions.append(f"COALESCE({_qi(source_col)}::text, '') !~* %s")
        params.append(r"(95\.81\.76\.62|127\.0\.0\.1|localhost)")

    if not conditions:
        conditions.append("TRUE")

    return " AND ".join(conditions), params


def _raw_7d_filter(cols):
    time_col = _first(cols, ["created_at", "visited_at", "timestamp", "visit_time", "time"])

    if time_col:
        return f"{_qi(time_col)} >= NOW() - INTERVAL '7 days'", []

    return "TRUE", []


def _leads_7d(connection):
    cols = _columns(connection, "leads")
    if not cols:
        return 0

    created_col = _first(cols, ["created_at", "created", "time"])
    trashed_col = _first(cols, ["trashed_at"])

    conditions = []
    params = []

    if created_col:
        conditions.append(f"{_qi(created_col)} >= NOW() - INTERVAL '7 days'")

    if trashed_col:
        conditions.append(f"{_qi(trashed_col)} IS NULL")

    where_sql = " AND ".join(conditions) if conditions else "TRUE"

    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(f"SELECT COUNT(*) AS count FROM leads WHERE {where_sql};", params)
    count = int(cursor.fetchone()["count"] or 0)
    cursor.close()

    return count


def register_clean_stats_routes(app, get_db_connection, verify_admin):
    @app.get("/admin/api/clean-stats")
    @app.get("/api/admin/clean-stats")
    async def api_admin_clean_stats(admin: str = Depends(verify_admin)):
        try:
            connection = get_db_connection()
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cols = _columns(connection, "site_visits")

            if not cols:
                cursor.close()
                connection.close()
                return JSONResponse(
                    {
                        "ok": False,
                        "error": "site_visits table not found",
                    },
                    status_code=200,
                )

            path_col = _first(cols, ["path", "url_path", "page_path", "page", "request_path"])
            source_col = _first(cols, ["source", "referrer_source", "referrer", "referer"])
            device_col = _first(cols, ["device_type", "device", "device_category"])
            browser_col = _first(cols, ["browser", "browser_name"])
            visitor_col = _first(cols, ["ip_hash", "visitor_hash", "session_hash", "visitor_id"])

            clean_7d_where, clean_7d_params = _build_filters(cols, days=7, today=False)
            clean_today_where, clean_today_params = _build_filters(cols, days=1, today=True)
            raw_7d_where, raw_7d_params = _raw_7d_filter(cols)

            clean_today = _count(cursor, clean_today_where, clean_today_params)
            clean_7d = _count(cursor, clean_7d_where, clean_7d_params)
            raw_7d = _count(cursor, raw_7d_where, raw_7d_params)
            excluded_7d = max(0, raw_7d - clean_7d)

            unique_7d = None
            if visitor_col:
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT {_qi(visitor_col)}) AS count
                    FROM site_visits
                    WHERE {clean_7d_where}
                      AND {_qi(visitor_col)} IS NOT NULL
                      AND {_qi(visitor_col)}::text <> '';
                    """,
                    clean_7d_params,
                )
                unique_7d = int(cursor.fetchone()["count"] or 0)

            request_7d = 0
            free_sketches_7d = 0
            projects_7d = 0

            if path_col:
                p = f"LOWER(COALESCE({_qi(path_col)}::text, ''))"

                cursor.execute(
                    f"SELECT COUNT(*) AS count FROM site_visits WHERE {clean_7d_where} AND {p} = '/request';",
                    clean_7d_params,
                )
                request_7d = int(cursor.fetchone()["count"] or 0)

                cursor.execute(
                    f"SELECT COUNT(*) AS count FROM site_visits WHERE {clean_7d_where} AND {p} = '/categories/free-sketches';",
                    clean_7d_params,
                )
                free_sketches_7d = int(cursor.fetchone()["count"] or 0)

                cursor.execute(
                    f"""
                    SELECT COUNT(*) AS count
                    FROM site_visits
                    WHERE {clean_7d_where}
                      AND ({p} = '/projects' OR {p} LIKE '/projects/%%' OR {p} LIKE '/project/%%');
                    """,
                    clean_7d_params,
                )
                projects_7d = int(cursor.fetchone()["count"] or 0)

            leads_7d = _leads_7d(connection)

            top_pages = []
            if path_col:
                top_pages = _rows(
                    cursor,
                    f"COALESCE({_qi(path_col)}::text, '/')",
                    clean_7d_where,
                    clean_7d_params,
                    limit=12,
                )

            sources = []
            if source_col:
                sources = _rows(
                    cursor,
                    f"COALESCE(NULLIF({_qi(source_col)}::text, ''), 'direct')",
                    clean_7d_where,
                    clean_7d_params,
                    limit=12,
                )

            devices = []
            if device_col:
                devices = _rows(
                    cursor,
                    f"COALESCE(NULLIF({_qi(device_col)}::text, ''), 'unknown')",
                    clean_7d_where,
                    clean_7d_params,
                    limit=8,
                )

            browsers = []
            if browser_col:
                browsers = _rows(
                    cursor,
                    f"COALESCE(NULLIF({_qi(browser_col)}::text, ''), 'unknown')",
                    clean_7d_where,
                    clean_7d_params,
                    limit=8,
                )

            cursor.close()
            connection.close()

            return JSONResponse(
                {
                    "ok": True,
                    "filters": {
                        "description": "Публичные страницы без админки, API, статики, сканеров, curl, ботов и технических запросов.",
                        "raw_7d": raw_7d,
                        "excluded_7d": excluded_7d,
                    },
                    "cards": {
                        "clean_today": clean_today,
                        "clean_7d": clean_7d,
                        "unique_7d": unique_7d,
                        "request_7d": request_7d,
                        "leads_7d": leads_7d,
                        "free_sketches_7d": free_sketches_7d,
                        "projects_7d": projects_7d,
                    },
                    "tables": {
                        "top_pages": top_pages,
                        "sources": sources,
                        "devices": devices,
                        "browsers": browsers,
                    },
                    "detected_columns": {
                        "path": path_col,
                        "source": source_col,
                        "device": device_col,
                        "browser": browser_col,
                        "visitor": visitor_col,
                    },
                }
            )

        except Exception as exc:
            return JSONResponse(
                {
                    "ok": False,
                    "error": repr(exc),
                },
                status_code=200,
            )
