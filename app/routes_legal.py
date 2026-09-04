import html
from typing import Optional

import psycopg2.extras
from fastapi import Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse


LEGAL_DEFAULTS = {
    "operator_name": "Владелец проекта ArtToSlipAway",
    "operator_status": "Указать правовой статус оператора",
    "operator_email": "privacy@example.com",
    "operator_city": "Указать город",
    "site_domain": "arttoslipaway.art",
    "publication_date": "Указать дату",
    "operator_legal_address": "Указать адрес",
    "rkn_registry_number": "Указать при наличии",
    "rkn_notification_date": "Указать при наличии",
    "rkn_registry_date": "Указать при наличии",
    "rkn_registry_order": "Указать при наличии",
    "rkn_db_location": "Россия",
    "rkn_cross_border_transfer": "нет",
}


def esc(value: str) -> str:
    return html.escape(str(value or ""))


def register_legal_routes(app, templates, get_db_connection, verify_admin):
    def get_legal_settings() -> dict:
        settings = dict(LEGAL_DEFAULTS)

        try:
            connection = get_db_connection()
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cursor.execute("""
                SELECT setting_key, setting_value
                FROM legal_settings;
            """)

            for row in cursor.fetchall():
                settings[row["setting_key"]] = row["setting_value"]

            cursor.close()
            connection.close()
        except Exception:
            pass

        return settings


    def render_legal_page(
        request: Request,
        title: str,
        content: str,
        description: str,
    ):
        return templates.TemplateResponse(
            request=request,
            name="legal_page.html",
            context={
                "title": title,
                "content": content,
                "description": description,
            }
        )


    @app.get("/privacy", response_class=HTMLResponse)
    async def privacy_page(request: Request):
        legal = get_legal_settings()

        operator_name = esc(legal.get("operator_name"))
        operator_status = esc(legal.get("operator_status"))
        operator_email = esc(legal.get("operator_email"))
        operator_city = esc(legal.get("operator_city"))
        site_domain = esc(legal.get("site_domain"))
        publication_date = esc(legal.get("publication_date"))
        operator_legal_address = esc(legal.get("operator_legal_address", ""))
        rkn_registry_number = esc(legal.get("rkn_registry_number", ""))
        rkn_notification_date = esc(legal.get("rkn_notification_date", ""))
        rkn_registry_date = esc(legal.get("rkn_registry_date", ""))
        rkn_registry_order = esc(legal.get("rkn_registry_order", ""))
        rkn_db_location = esc(legal.get("rkn_db_location", ""))
        rkn_cross_border_transfer = esc(legal.get("rkn_cross_border_transfer", ""))

        content = f"""
            <h1>Политика обработки персональных данных</h1>

            <div class="warning">
                Актуальная редакция документа размещена на сайте. Оператор внесён в реестр операторов персональных данных Роскомнадзора.
            </div>

            <p>
                Настоящая Политика определяет порядок обработки и защиты персональных данных пользователей сайта
                <strong>{site_domain}</strong>, принадлежащего проекту <strong>{operator_name}</strong>.
            </p>

            <h2>1. Оператор персональных данных</h2>
            <p>
                Оператор: <strong>{operator_name}</strong><br>
                Статус: <strong>{operator_status}</strong><br>
                Город работы: <strong>{operator_city}</strong><br>
                Юридический адрес / регион регистрации: <strong>{operator_legal_address}</strong><br>
                Email для обращений по персональным данным: <strong>{operator_email}</strong>
            </p>

            <!-- RKN_OPERATOR_REGISTRY_INFO_START -->
            <h2>1.1. Сведения о регистрации в реестре Роскомнадзора</h2>
            <p>
                Регистрационный номер в реестре операторов персональных данных Роскомнадзора:
                <strong>{rkn_registry_number}</strong><br>
                Дата регистрации уведомления: <strong>{rkn_notification_date}</strong><br>
                Дата внесения в реестр: <strong>{rkn_registry_date}</strong><br>
                Основание внесения: <strong>{rkn_registry_order}</strong><br>
                Местонахождение базы данных: <strong>{rkn_db_location}</strong><br>
                Трансграничная передача персональных данных: <strong>{rkn_cross_border_transfer}</strong>
            </p>
            <!-- RKN_OPERATOR_REGISTRY_INFO_END -->

            <p>
            </p>

            <h2>2. Какие данные обрабатываются</h2>
            <ul>
                <li>имя или псевдоним;</li>
                <li>контакт для связи: Telegram, телефон, email или иной указанный способ;</li>
                <li>город и предпочтительные даты записи;</li>
                <li>описание идеи татуировки, картины, мерча или иного проекта;</li>
                <li>зона тела, примерный размер, стиль и иные параметры заявки;</li>
                <li>файлы-референсы, изображения, PDF-файлы;</li>
                <li>выбранный свободный эскиз или проект;</li>
                <li>технические данные: IP-адрес, User-Agent, дата и время запроса.</li>
            </ul>

            <h2>3. Цели обработки</h2>
            <ul>
                <li>обработка заявки пользователя;</li>
                <li>обратная связь по татуировке, картине, мерчу или консультации;</li>
                <li>подбор даты записи;</li>
                <li>подготовка эскиза, проекта или консультации;</li>
                <li>ведение внутренней истории заявок;</li>
                <li>обеспечение безопасности сайта и предотвращение злоупотреблений.</li>
            </ul>

            <h2>4. Правовые основания обработки</h2>
            <p>
                Обработка персональных данных осуществляется на основании согласия пользователя,
                а также для подготовки, заключения и исполнения гражданско-правового договора.
            </p>

            <h2>4.1. Веб-аналитика</h2>
            <p>
                На сайте может использоваться сервис Google Analytics для анализа посещаемости,
                источников переходов и поведения пользователей на страницах сайта.
                Google Analytics включается только после согласия пользователя через cookie-баннер.
            </p>
            <p>
                До получения согласия сайт не загружает скрипт Google Analytics.
                Пользователь может отказаться от аналитики, выбрав вариант «Только необходимые».
                В этом случае используются только технические cookies, необходимые для работы сайта.
            </p>

            <h2>5. Действия с персональными данными</h2>
            <p>
                Оператор может осуществлять сбор, запись, систематизацию, накопление, хранение,
                уточнение, использование, передачу в технически необходимом объёме,
                блокирование, удаление и уничтожение персональных данных.
            </p>

            <h2>6. Срок хранения</h2>
            <p>
                Данные хранятся до достижения целей обработки либо до отзыва согласия пользователем,
                если иное хранение не требуется по закону.
            </p>

            <h2>7. Передача третьим лицам</h2>
            <p>
                Персональные данные не передаются третьим лицам без необходимости и законного основания.
                Доступ может быть предоставлен хостинг-провайдеру и техническим сервисам сайта
                в объёме, необходимом для функционирования сервиса.
            </p>

            <h2>8. Меры защиты</h2>
            <p>
                Доступ к админке ограничен, используется парольная аутентификация,
                HTTPS, firewall, Fail2Ban, ограничение доступа к PostgreSQL с localhost,
                контроль типов загружаемых файлов и резервное копирование.
            </p>

            <h2>9. Права пользователя</h2>
            <p>
                Пользователь вправе запросить информацию об обработке своих персональных данных,
                потребовать уточнения, блокирования или удаления данных, а также отозвать согласие.
                Для обращения используется email: <strong>{operator_email}</strong>.
            </p>

            <p class="muted">Дата публикации: {publication_date}</p>
        """

        return render_legal_page(
            request,
            "Политика обработки персональных данных",
            content,
            "Политика ArtToSlipAway: порядок сбора, использования, хранения и защиты персональных данных пользователей сайта.",
        )


    @app.get("/consent", response_class=HTMLResponse)
    async def consent_page(request: Request):
        legal = get_legal_settings()

        operator_name = esc(legal.get("operator_name"))
        operator_email = esc(legal.get("operator_email"))
        site_domain = esc(legal.get("site_domain"))
        publication_date = esc(legal.get("publication_date"))
        rkn_registry_number = esc(legal.get("rkn_registry_number", ""))
        rkn_notification_date = esc(legal.get("rkn_notification_date", ""))

        content = f"""
            <h1>Согласие на обработку персональных данных</h1>

            <p>
                Пользователь, отправляя форму заявки на сайте <strong>{site_domain}</strong>,
                свободно, своей волей и в своём интересе даёт согласие оператору
                <strong>{operator_name}</strong> на обработку своих персональных данных.
            </p>

            <!-- RKN_CONSENT_OPERATOR_INFO_START -->
            <p>
                Сведения об операторе внесены в реестр операторов персональных данных Роскомнадзора.
                Регистрационный номер: <strong>{rkn_registry_number}</strong>.
                Дата регистрации уведомления: <strong>{rkn_notification_date}</strong>.
            </p>
            <!-- RKN_CONSENT_OPERATOR_INFO_END -->

            <h2>1. Персональные данные</h2>
            <ul>
                <li>имя или псевдоним;</li>
                <li>контактные данные;</li>
                <li>город, предпочтительные даты и способ связи;</li>
                <li>описание идеи, проекта, зоны тела, размера, стиля;</li>
                <li>прикреплённые референсы и изображения;</li>
                <li>выбранный свободный эскиз или проект;</li>
                <li>технические данные обращения к сайту.</li>
            </ul>

            <h2>2. Цели обработки</h2>
            <ul>
                <li>рассмотрение заявки;</li>
                <li>связь с пользователем;</li>
                <li>подготовка консультации, эскиза или записи;</li>
                <li>ведение истории обращений;</li>
                <li>обеспечение безопасности сайта.</li>
            </ul>

            <h2>3. Срок действия согласия</h2>
            <p>
                Согласие действует до достижения целей обработки или до его отзыва пользователем.
                Отзыв можно направить на email: <strong>{operator_email}</strong>.
            </p>

            <p class="muted">Дата публикации: {publication_date}</p>
        """

        return render_legal_page(
            request,
            "Согласие на обработку персональных данных",
            content,
            "Согласие пользователя сайта ArtToSlipAway на обработку персональных данных: цели, состав данных, срок действия и порядок отзыва.",
        )


    @app.get("/terms", response_class=HTMLResponse)
    async def terms_page(request: Request):
        legal = get_legal_settings()

        operator_name = esc(legal.get("operator_name"))
        publication_date = esc(legal.get("publication_date"))

        content = f"""
            <h1>Условия записи и работы</h1>

            <p>
                Настоящие условия описывают общий порядок взаимодействия с проектом
                <strong>{operator_name}</strong> при обращении за татуировкой, эскизом,
                картиной, мерчем или консультацией.
            </p>

            <h2>1. Заявка</h2>
            <p>
                Отправка заявки через сайт не является автоматическим бронированием даты.
                Заявка рассматривается мастером, после чего пользователь получает ответ по указанному контакту.
            </p>

            <h2>2. Эскизы и проекты</h2>
            <p>
                Свободные эскизы и проекты могут быть адаптированы под тело, размер,
                композицию и технические особенности работы.
            </p>

            <h2>3. Предоплата</h2>
            <p>
                Дата записи и разработка проекта могут фиксироваться по предоплате.
                Конкретные условия согласовываются отдельно до записи.
            </p>

            <h2>4. Авторские права</h2>
            <p>
                Эскизы, изображения, тексты, фотографии работ и визуальные материалы проекта ArtToSlipAway
                являются объектами авторского права, если не указано иное.
            </p>

            <p class="muted">Дата публикации: {publication_date}</p>
        """

        return render_legal_page(
            request,
            "Условия записи и работы",
            content,
            "Условия записи и работы ArtToSlipAway: обсуждение проекта, предоплата, перенос записи, подготовка, сроки и авторские права.",
        )


    @app.get("/cookies", response_class=HTMLResponse)
    async def cookies_page(request: Request):
        legal = get_legal_settings()

        site_domain = esc(legal.get("site_domain"))
        publication_date = esc(legal.get("publication_date"))

        content = f"""
            <h1>Уведомление о cookies</h1>

            <p>
                Сайт <strong>{site_domain}</strong> может использовать технические cookies,
                необходимые для корректной работы сайта и админ-панели.
            </p>

            <h2>1. Какие cookies используются</h2>
            <ul>
                <li>технические cookies для работы административной сессии;</li>
                <li>служебные данные браузера и сервера;</li>
                <li>cookies аналитики Google Analytics — используются только после согласия пользователя через cookie-баннер;</li>
                <li>cookie <code>ats_analytics_consent</code> — хранит выбор пользователя: разрешить аналитику или оставить только необходимые cookies.</li>
            </ul>

            <h2>2. Управление cookies</h2>
            <p>
                Пользователь может ограничить или удалить cookies в настройках браузера.
                Это может повлиять на работу отдельных функций сайта.
            </p>

            <p class="muted">Дата публикации: {publication_date}</p>
        """

        return render_legal_page(
            request,
            "Уведомление о cookies",
            content,
            "Уведомление ArtToSlipAway об использовании cookies: какие технические и аналитические данные применяются и как управлять cookies в браузере.",
        )


    @app.get("/admin/legal", response_class=HTMLResponse)
    async def admin_legal_settings(
        request: Request,
        saved: Optional[str] = None,
        admin: str = Depends(verify_admin)
    ):
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        for key, value in LEGAL_DEFAULTS.items():
            cursor.execute("""
                INSERT INTO legal_settings (setting_key, setting_value)
                VALUES (%s, %s)
                ON CONFLICT (setting_key) DO NOTHING;
            """, (key, value))

        connection.commit()

        cursor.execute("""
            SELECT setting_key, setting_value
            FROM legal_settings;
        """)

        settings = dict(LEGAL_DEFAULTS)

        for row in cursor.fetchall():
            settings[row["setting_key"]] = row["setting_value"]

        cursor.close()
        connection.close()

        return templates.TemplateResponse(
            request=request,
            name="admin_legal.html",
            context={
                "title": "Юридические настройки",
                "settings": settings,
                "saved": bool(saved)
            }
        )


    @app.post("/admin/legal")
    async def admin_legal_settings_save(
        operator_name: str = Form(...),
        operator_status: str = Form(""),
        operator_email: str = Form(...),
        operator_city: str = Form(""),
        site_domain: str = Form(""),
        publication_date: str = Form(""),
        admin: str = Depends(verify_admin)
    ):
        values = {
            "operator_name": operator_name.strip(),
            "operator_status": operator_status.strip(),
            "operator_email": operator_email.strip(),
            "operator_city": operator_city.strip(),
            "site_domain": site_domain.strip(),
            "publication_date": publication_date.strip(),
        }

        connection = get_db_connection()
        cursor = connection.cursor()

        for key, value in values.items():
            cursor.execute("""
                INSERT INTO legal_settings (setting_key, setting_value, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (setting_key)
                DO UPDATE SET
                    setting_value = EXCLUDED.setting_value,
                    updated_at = CURRENT_TIMESTAMP;
            """, (key, value))

        connection.commit()
        cursor.close()
        connection.close()

        return RedirectResponse(
            url="/admin/legal?saved=1",
            status_code=status.HTTP_303_SEE_OTHER
        )
