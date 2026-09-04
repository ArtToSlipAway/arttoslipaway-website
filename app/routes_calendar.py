import time
import threading
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
import psycopg2
import psycopg2.extras
from fastapi import Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.paths import PROJECT_ROOT
from app.auth import verify_admin
from app.db import get_db_connection
from app.views import templates
from fastapi import APIRouter

router = APIRouter()

GOOGLE_CALENDAR_FILE = os.getenv(
    "GOOGLE_CALENDAR_CREDENTIALS_FILE",
    str(PROJECT_ROOT / "credentials" / "google-calendar.json"),
)

GOOGLE_CALENDARS = {
    "work": os.getenv("GOOGLE_CALENDAR_WORK_ID", "").strip(),
    "tattoo": os.getenv("GOOGLE_CALENDAR_TATTOO_ID", "").strip(),
}


def get_google_calendar_service():
    credentials_path = Path(GOOGLE_CALENDAR_FILE)
    if not credentials_path.is_file():
        return None

    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )

    return build(
        "calendar",
        "v3",
        credentials=creds
    )


# ATS_CITY_TIME_WINDOWS_V1
#
# Публичное рабочее окно студии:
# 10:00–23:00, Europe/Moscow.
#
# Google Calendar теперь возвращает не просто
# занятые даты, а реальные временные интервалы.
#
# OZON:
#   блокирует только фактическое время смены.
#
# Tattoo:
#   блокирует только события с "тату"/"сеанс"
#   и только фактическое время события.

_SPB_PUBLIC_TZ = timezone(
    timedelta(hours=3)
)

_STUDIO_START_MINUTE = 10 * 60
_STUDIO_END_MINUTE = 23 * 60


def _ats_minutes_label(value):
    hours = value // 60
    minutes = value % 60

    return f"{hours:02d}:{minutes:02d}"


def _ats_copy_busy_intervals(data):
    return {
        day: list(intervals)
        for day, intervals in data.items()
    }


def _ats_add_busy_interval(
    busy,
    day,
    start_minute,
    end_minute
):
    start_minute = max(
        _STUDIO_START_MINUTE,
        int(start_minute)
    )

    end_minute = min(
        _STUDIO_END_MINUTE,
        int(end_minute)
    )

    if end_minute <= start_minute:
        return

    busy.setdefault(
        day.isoformat(),
        []
    ).append(
        (
            start_minute,
            end_minute
        )
    )


def _ats_google_datetime(value):
    if not value:
        return None

    value = value.replace(
        "Z",
        "+00:00"
    )

    return (
        datetime
        .fromisoformat(value)
        .astimezone(_SPB_PUBLIC_TZ)
    )


def _ats_add_google_event(
    busy,
    event
):
    start = event.get(
        "start",
        {}
    )

    end = event.get(
        "end",
        {}
    )

    start_dt_value = start.get(
        "dateTime"
    )

    end_dt_value = end.get(
        "dateTime"
    )

    # Обычное событие с точным временем.
    if start_dt_value and end_dt_value:
        start_dt = _ats_google_datetime(
            start_dt_value
        )

        end_dt = _ats_google_datetime(
            end_dt_value
        )

        if (
            not start_dt
            or not end_dt
            or end_dt <= start_dt
        ):
            return

        current_day = start_dt.date()
        last_day = end_dt.date()

        while current_day <= last_day:

            if current_day == start_dt.date():
                start_minute = (
                    start_dt.hour * 60
                    + start_dt.minute
                )
            else:
                start_minute = 0

            if current_day == end_dt.date():
                end_minute = (
                    end_dt.hour * 60
                    + end_dt.minute
                )
            else:
                end_minute = 24 * 60

            _ats_add_busy_interval(
                busy,
                current_day,
                start_minute,
                end_minute
            )

            current_day += timedelta(
                days=1
            )

        return

    # Google all-day event.
    start_date_value = start.get(
        "date"
    )

    end_date_value = end.get(
        "date"
    )

    if (
        not start_date_value
        or not end_date_value
    ):
        return

    start_day = (
        datetime
        .fromisoformat(start_date_value)
        .date()
    )

    # У Google end.date для all-day exclusive.
    end_day = (
        datetime
        .fromisoformat(end_date_value)
        .date()
    )

    current_day = start_day

    while current_day < end_day:
        _ats_add_busy_interval(
            busy,
            current_day,
            _STUDIO_START_MINUTE,
            _STUDIO_END_MINUTE
        )

        current_day += timedelta(
            days=1
        )


def _ats_merge_intervals(intervals):
    if not intervals:
        return []

    ordered = sorted(
        (
            int(start),
            int(end)
        )
        for start, end in intervals
        if end > start
    )

    merged = []

    for start, end in ordered:

        if (
            not merged
            or start > merged[-1][1]
        ):
            merged.append(
                [start, end]
            )

            continue

        merged[-1][1] = max(
            merged[-1][1],
            end
        )

    return [
        (start, end)
        for start, end in merged
    ]


def get_busy_intervals_from_google():
    configured_calendars = {
        name: calendar_id
        for name, calendar_id in GOOGLE_CALENDARS.items()
        if calendar_id
    }
    if not configured_calendars:
        return {}

    service = get_google_calendar_service()
    if service is None:
        return {}

    busy = {}

    now_utc = datetime.now(
        timezone.utc
    )

    future_utc = (
        now_utc
        + timedelta(days=90)
    )

    for calendar_name, calendar_id in (
        configured_calendars.items()
    ):

        events = (
            service
            .events()
            .list(
                calendarId=calendar_id,
                timeMin=now_utc.isoformat(),
                timeMax=future_utc.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            )
            .execute()
        )

        for event in events.get(
            "items",
            []
        ):

            if (
                event.get("status")
                == "cancelled"
            ):
                continue

            title = (
                event
                .get("summary", "")
                .lower()
            )

            if calendar_name == "work":
                # Любая смена OZON блокирует
                # только своё фактическое время.
                pass

            elif calendar_name == "tattoo":

                if not any(
                    word in title
                    for word in (
                        "сеанс",
                        "тату"
                    )
                ):
                    continue

            else:
                continue

            _ats_add_google_event(
                busy,
                event
            )

    return {
        day: _ats_merge_intervals(
            intervals
        )
        for day, intervals
        in busy.items()
    }


# Google — медленная внешняя часть API.
# Храним результат максимум 60 секунд.

_CITY_SLOTS_GOOGLE_CACHE_TTL = 60.0

_city_slots_google_cache = {
    "expires_at": 0.0,
    "busy_intervals": None,
}

_city_slots_google_cache_lock = (
    threading.Lock()
)


def get_busy_intervals_from_google_cached():
    now = time.monotonic()

    cached = (
        _city_slots_google_cache[
            "busy_intervals"
        ]
    )

    if (
        cached is not None
        and now
        < _city_slots_google_cache[
            "expires_at"
        ]
    ):
        return _ats_copy_busy_intervals(
            cached
        )

    with _city_slots_google_cache_lock:

        now = time.monotonic()

        cached = (
            _city_slots_google_cache[
                "busy_intervals"
            ]
        )

        if (
            cached is not None
            and now
            < _city_slots_google_cache[
                "expires_at"
            ]
        ):
            return _ats_copy_busy_intervals(
                cached
            )

        try:
            busy_intervals = (
                get_busy_intervals_from_google()
            )

        except Exception:

            if cached is not None:
                return _ats_copy_busy_intervals(
                    cached
                )

            raise

        _city_slots_google_cache[
            "busy_intervals"
        ] = _ats_copy_busy_intervals(
            busy_intervals
        )

        _city_slots_google_cache[
            "expires_at"
        ] = (
            time.monotonic()
            + _CITY_SLOTS_GOOGLE_CACHE_TTL
        )

        return _ats_copy_busy_intervals(
            busy_intervals
        )


def _ats_available_windows(
    day,
    busy_intervals,
    local_now
):
    start_minute = (
        _STUDIO_START_MINUTE
    )

    end_minute = (
        _STUDIO_END_MINUTE
    )

    # Сегодня нельзя предлагать уже
    # прошедшую часть рабочего дня.
    if day < local_now.date():
        return []

    if day == local_now.date():

        current_minute = (
            local_now.hour * 60
            + local_now.minute
        )

        if (
            local_now.second
            or local_now.microsecond
        ):
            current_minute += 1

        start_minute = max(
            start_minute,
            current_minute
        )

    if start_minute >= end_minute:
        return []

    merged_busy = _ats_merge_intervals(
        busy_intervals.get(
            day.isoformat(),
            []
        )
    )

    windows = []
    cursor = start_minute

    for busy_start, busy_end in merged_busy:

        if busy_end <= cursor:
            continue

        if busy_start >= end_minute:
            break

        if busy_start > cursor:
            windows.append(
                (
                    cursor,
                    min(
                        busy_start,
                        end_minute
                    )
                )
            )

        cursor = max(
            cursor,
            busy_end
        )

        if cursor >= end_minute:
            break

    if cursor < end_minute:
        windows.append(
            (
                cursor,
                end_minute
            )
        )

    return [
        (start, end)
        for start, end in windows
        if end > start
    ]


def _ats_windows_payload(windows):
    return [
        {
            "start": _ats_minutes_label(
                start
            ),
            "end": _ats_minutes_label(
                end
            )
        }
        for start, end in windows
    ]


def _ats_windows_label(windows):
    if not windows:
        return ""

    if len(windows) == 1:

        start, end = windows[0]

        if (
            start == _STUDIO_START_MINUTE
            and end == _STUDIO_END_MINUTE
        ):
            return "10:00–23:00"

        if (
            start == _STUDIO_START_MINUTE
            and end < _STUDIO_END_MINUTE
        ):
            return (
                "до "
                + _ats_minutes_label(end)
            )

        if (
            start > _STUDIO_START_MINUTE
            and end == _STUDIO_END_MINUTE
        ):
            return (
                "после "
                + _ats_minutes_label(start)
            )

        return (
            _ats_minutes_label(start)
            + "–"
            + _ats_minutes_label(end)
        )

    return " / ".join(
        (
            _ats_minutes_label(start)
            + "–"
            + _ats_minutes_label(end)
        )
        for start, end in windows
    )


# === END GOOGLE CALENDAR SYNC ===



@router.get("/api/city-slots")
def api_city_slots():

    busy_intervals = (
        get_busy_intervals_from_google_cached()
    )

    local_now = (
        datetime
        .now(timezone.utc)
        .astimezone(_SPB_PUBLIC_TZ)
    )

    today = local_now.date()

    connection = get_db_connection()

    cursor = connection.cursor(
        cursor_factory=
            psycopg2.extras.RealDictCursor
    )

    cursor.execute("""
        SELECT
            id,
            city,
            date_label,
            slot_date,
            slot_time,
            status,
            note
        FROM city_slots
        WHERE status IN (
            'available',
            'booked'
        )
        ORDER BY
            slot_date ASC NULLS LAST;
    """)

    manual_slots = cursor.fetchall()

    cursor.close()
    connection.close()

    result = {
        "spb": [],
        "smolensk": [],
        "moscow": []
    }


    # ------------------------------
    # Ручные записи из админки
    # ------------------------------

    for row in manual_slots:

        city = row["city"]

        if city not in result:
            continue

        slot_date = row[
            "slot_date"
        ]

        if (
            slot_date
            and slot_date < today
        ):
            continue

        status_value = row[
            "status"
        ]

        # Москва / Смоленск пока
        # остаются как раньше.
        if (
            city != "spb"
            or not slot_date
        ):
            result[city].append({
                "id": row["id"],
                "city": city,
                "date_label":
                    row["date_label"],
                "slot_date": (
                    slot_date.isoformat()
                    if slot_date
                    else None
                ),
                "slot_time":
                    row["slot_time"],
                "status":
                    status_value
            })

            continue

        # Ручной booked должен
        # продолжать блокировать дату.
        if status_value == "booked":

            result["spb"].append({
                "id": row["id"],
                "city": "spb",
                "date_label":
                    row["date_label"],
                "slot_date":
                    slot_date.isoformat(),
                "slot_time":
                    row["slot_time"],
                "status": "booked",
                "available_windows": []
            })

            continue

        windows = _ats_available_windows(
            slot_date,
            busy_intervals,
            local_now
        )

        if not windows:
            continue

        result["spb"].append({
            "id": row["id"],
            "city": "spb",
            "date_label":
                row["date_label"],
            "slot_date":
                slot_date.isoformat(),
            "slot_time":
                _ats_windows_label(
                    windows
                ),
            "status": "available",
            "available_windows":
                _ats_windows_payload(
                    windows
                )
        })


    # ------------------------------
    # Автоматические даты СПб
    # ------------------------------

    first_month = today.replace(
        day=1
    )

    first_after_next_month = (
        first_month
        + timedelta(days=70)
    ).replace(
        day=1
    )

    last_next_month = (
        first_after_next_month
        - timedelta(days=1)
    )

    total_days = (
        last_next_month
        - today
    ).days + 1

    for i in range(total_days):

        day = (
            today
            + timedelta(days=i)
        )

        day_str = day.isoformat()

        exists = any(
            item.get("slot_date")
            == day_str
            for item
            in result["spb"]
        )

        if exists:
            continue

        windows = _ats_available_windows(
            day,
            busy_intervals,
            local_now
        )

        if not windows:
            continue

        result["spb"].append({
            "id": None,
            "city": "spb",
            "date_label":
                day.strftime(
                    "%d.%m.%Y"
                ),
            "slot_date":
                day_str,
            "slot_time":
                _ats_windows_label(
                    windows
                ),
            "status":
                "available",
            "available_windows":
                _ats_windows_payload(
                    windows
                )
        })


    result["spb"] = sorted(
        result["spb"],
        key=lambda item:
            item.get("slot_date")
            or "9999"
    )

    return result


# === /city slots api ===


# === city slots admin ===

@router.get("/admin/city-slots", response_class=HTMLResponse)
async def admin_city_slots(request: Request, admin: str = Depends(verify_admin)):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT
            id,
            city,
            date_label,
            slot_date,
            slot_time,
            status,
            note,
            sort_order,
            created_at,
            updated_at
        FROM city_slots
        ORDER BY
            city,
            sort_order ASC,
            slot_date ASC NULLS LAST,
            id ASC;
    """)

    slots = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_city_slots.html",
        context={
            "title": "Свободные даты",
            "slots": slots
        }
    )


@router.post("/admin/city-slots")
async def admin_city_slot_create(
    city: str = Form(...),
    date_label: str = Form(...),
    slot_date: str = Form(""),
    slot_time: str = Form(""),
    status_value: str = Form("available"),
    note: str = Form(""),
    sort_order: int = Form(100),
    admin: str = Depends(verify_admin)
):
    if city not in {"spb", "smolensk", "moscow"}:
        raise HTTPException(status_code=400, detail="Недопустимый город")

    if status_value not in {"available", "hidden", "booked"}:
        raise HTTPException(status_code=400, detail="Недопустимый статус")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO city_slots (
            city,
            date_label,
            slot_date,
            slot_time,
            status,
            note,
            sort_order,
            updated_at
        )
        VALUES (%s, %s, NULLIF(%s, '')::date, NULLIF(%s, ''), %s, NULLIF(%s, ''), %s, CURRENT_TIMESTAMP);
    """, (
        city,
        date_label.strip(),
        slot_date.strip(),
        slot_time.strip(),
        status_value,
        note.strip(),
        sort_order
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/city-slots",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/city-slots/{slot_id}/edit")
async def admin_city_slot_edit(
    slot_id: int,
    city: str = Form(...),
    date_label: str = Form(...),
    slot_date: str = Form(""),
    slot_time: str = Form(""),
    status_value: str = Form("available"),
    note: str = Form(""),
    sort_order: int = Form(100),
    admin: str = Depends(verify_admin)
):
    if city not in {"spb", "smolensk", "moscow"}:
        raise HTTPException(status_code=400, detail="Недопустимый город")

    if status_value not in {"available", "hidden", "booked"}:
        raise HTTPException(status_code=400, detail="Недопустимый статус")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE city_slots
        SET
            city = %s,
            date_label = %s,
            slot_date = NULLIF(%s, '')::date,
            slot_time = NULLIF(%s, ''),
            status = %s,
            note = NULLIF(%s, ''),
            sort_order = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    """, (
        city,
        date_label.strip(),
        slot_date.strip(),
        slot_time.strip(),
        status_value,
        note.strip(),
        sort_order,
        slot_id
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/city-slots",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/admin/city-slots/{slot_id}/delete")
async def admin_city_slot_delete(
    slot_id: int,
    admin: str = Depends(verify_admin)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM city_slots WHERE id = %s;", (slot_id,))

    connection.commit()
    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/admin/city-slots",
        status_code=status.HTTP_303_SEE_OTHER
    )

# === /city slots admin ===


# === project media api ===


# Home page carousel media block key
