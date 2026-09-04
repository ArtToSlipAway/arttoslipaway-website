import inspect
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.paths import BACKUPS_DIR, PROJECT_ROOT

def _run(command, timeout=12):
    try:
        result = subprocess.run(
            command,
            shell=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return result.stdout.strip()
    except Exception as exc:
        return f"ERROR: {exc!r}"


def _latest_backups(limit=15):
    if not BACKUPS_DIR.is_dir():
        return "Каталог резервных копий не создан"

    entries = sorted(
        BACKUPS_DIR.iterdir(),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:limit]
    return "\n".join(path.name for path in entries)


async def _is_admin(request, verify_admin):
    try:
        result = verify_admin(request)
        if inspect.isawaitable(result):
            result = await result
        return bool(result)
    except Exception:
        return False


def _dir_size(path):
    try:
        total = 0
        for root, dirs, files in os.walk(path):
            for name in files:
                try:
                    total += os.path.getsize(os.path.join(root, name))
                except OSError:
                    pass
        return total
    except Exception:
        return 0


def _human_size(num):
    for unit in ["B", "K", "M", "G", "T"]:
        if num < 1024:
            return f"{num:.1f}{unit}"
        num /= 1024
    return f"{num:.1f}P"


def register_admin_system_routes(app, templates, verify_admin):
    @app.get("/admin/system", response_class=HTMLResponse)
    async def admin_system(request: Request):
        if not await _is_admin(request, verify_admin):
            return RedirectResponse(url="/admin/login", status_code=303)

        disk = shutil.disk_usage("/")
        disk_used_percent = round((disk.used / disk.total) * 100, 1)

        data = {
            "request": request,
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "disk_total": _human_size(disk.total),
            "disk_used": _human_size(disk.used),
            "disk_free": _human_size(disk.free),
            "disk_used_percent": disk_used_percent,
            "backups_size": _human_size(_dir_size(BACKUPS_DIR)),
            "service_status": _run(["systemctl", "is-active", "arttoslipaway.service"]),
            "nginx_status": _run(["systemctl", "is-active", "nginx"]),
            "postgres_status": _run(["systemctl", "is-active", "postgresql"]),
            "uptime": _run(["uptime", "-p"]),
            "memory": _run(["free", "-h"]),
            "disk_df": _run(["df", "-h", "/"]),
            "latest_backups": _latest_backups(),
            "journal": _run([
                "journalctl",
                "-u",
                "arttoslipaway.service",
                "--since",
                "30 minutes ago",
                "--no-pager",
                "-n",
                "40",
                "-o",
                "cat",
            ]),
        }

        return templates.TemplateResponse(
            request=request,
            name="admin_system.html",
            context=data,
        )
