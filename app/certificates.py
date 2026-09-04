import psycopg2
import psycopg2.extras

CERTIFICATE_SETTINGS_DEFAULTS = {
    "certificate_info_title":
        "Информация о сертификате",

    "certificate_validity_text":
        "Срок действия сертификата — 6 месяцев с момента приобретения.",

    "certificate_min_nominal":
        "5000",

    "certificate_nominal_text":
        "Минимальный номинал равен минимальной стоимости сеанса —",

    "certificate_partial_payment_text":
        "Сертификат можно использовать для частичной оплаты сеанса.",

    "certificate_single_use_text":
        "Сертификатом можно воспользоваться один раз на протяжении срока его действия.",

    "certificate_button_text":
        "Приобрести сертификат",
}


def get_certificate_settings(connection):
    settings = dict(
        CERTIFICATE_SETTINGS_DEFAULTS
    )

    settings_cursor = connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    try:
        settings_cursor.execute(
            """
            SELECT
                setting_key,
                setting_value
            FROM site_settings
            WHERE setting_key = ANY(%s);
            """,
            (
                list(
                    CERTIFICATE_SETTINGS_DEFAULTS.keys()
                ),
            ),
        )

        for row in settings_cursor.fetchall():
            value = row["setting_value"]

            if value is not None:
                settings[row["setting_key"]] = value

    finally:
        settings_cursor.close()

    return settings


def get_certificate_min_nominal(settings):
    try:
        value = int(
            str(
                settings.get(
                    "certificate_min_nominal",
                    "5000",
                )
            ).strip()
        )
    except (TypeError, ValueError):
        value = 5000

    if value < 1:
        value = 5000

    return value
