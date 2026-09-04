import os
import ssl
import smtplib
from pathlib import Path
from email.message import EmailMessage
from email.header import Header
from email.utils import formataddr
from datetime import datetime

from app.paths import ENV_PATH

def _load_env_file():
    if not ENV_PATH.exists():
        return

    for line in ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def _clean(value):
    if value is None:
        return ""

    value = str(value).strip()

    if value.lower() in {"none", "null"}:
        return ""

    return value


def _field(data, key):
    if not data:
        return ""
    return _clean(data.get(key))


def _smtp_enabled():
    return os.environ.get("SMTP_ENABLED", "").strip().lower() == "true"


def send_new_lead_email(lead_id, lead_data=None, is_test=False):
    _load_env_file()

    if not _smtp_enabled():
        return False

    host = os.environ.get("SMTP_HOST", "smtp.yandex.ru").strip()
    port = int(os.environ.get("SMTP_PORT", "465").strip())
    use_ssl = os.environ.get("SMTP_USE_SSL", "true").strip().lower() == "true"

    username = os.environ.get("SMTP_USERNAME", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "")
    from_email = os.environ.get("SMTP_FROM_EMAIL", username).strip()
    from_name = os.environ.get("SMTP_FROM_NAME", "ArtToSlipAway").strip()
    to_email = os.environ.get("SMTP_ADMIN_TO", "").strip()

    if not username or not password or not to_email:
        raise RuntimeError("SMTP settings are incomplete")

    site_base = (
        os.environ.get("TELEGRAM_SITE_BASE_URL")
        or os.environ.get("SITE_BASE_URL")
        or "https://arttoslipaway.art"
    ).strip().rstrip("/")

    subject_prefix = "ТЕСТ: " if is_test else ""
    subject = f"{subject_prefix}Новая заявка #{lead_id} — ArtToSlipAway"

    rows = [
        ("ID заявки", lead_id),
        ("Имя", _field(lead_data, "name")),
        ("Контакт", _field(lead_data, "contact")),
        ("Способ связи", _field(lead_data, "contact_method")),
        ("Тип услуги", _field(lead_data, "service_type")),
        ("Тип заявки", _field(lead_data, "request_type")),
        ("Город", _field(lead_data, "city")),
        ("Интерес", _field(lead_data, "project_interest")),
        ("Место на теле", _field(lead_data, "body_place")),
        ("Размер", _field(lead_data, "approximate_size")),
        ("Стиль", _field(lead_data, "style_preference")),
        ("Перекрытие", _field(lead_data, "is_coverup")),
        ("Формат продукта", _field(lead_data, "product_format")),
        ("Срок", _field(lead_data, "deadline")),
        ("Бюджет", _field(lead_data, "budget_range")),
        ("Выбранная дата", _field(lead_data, "preferred_dates")),
        ("Выбранный медиа ID", _field(lead_data, "selected_media_id_value") or _field(lead_data, "selected_media_id")),
        ("Выбранный эскиз", _field(lead_data, "selected_sketch_title")),
        ("Страница входа", _field(lead_data, "entry_page")),
        ("Источник", _field(lead_data, "lead_source")),
    ]

    lines = []
    lines.append("Новая заявка с сайта ArtToSlipAway.")
    lines.append("")
    lines.append(f"Время уведомления: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    for label, value in rows:
        value = _clean(value)
        if value:
            lines.append(f"{label}: {value}")

    idea = _field(lead_data, "idea")
    message = _field(lead_data, "message")

    if idea:
        lines.append("")
        lines.append("Идея:")
        lines.append(idea)

    if message:
        lines.append("")
        lines.append("Комментарий:")
        lines.append(message)

    lines.append("")
    lines.append(f"Админка заявок: {site_base}/admin/leads")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((str(Header(from_name, "utf-8")), from_email))
    msg["To"] = to_email
    msg.set_content("\n".join(lines))

    context = ssl.create_default_context()

    if use_ssl:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as server:
            server.login(username, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls(context=context)
            server.login(username, password)
            server.send_message(msg)

    return True
