(function () {
    "use strict";

    if (!window.location.pathname.startsWith("/admin/stats")) {
        return;
    }

    var API_URL = "/admin/api/clean-stats";

    function addStyle() {
        if (document.getElementById("atsCleanStatsStyle")) {
            return;
        }

        var style = document.createElement("style");
        style.id = "atsCleanStatsStyle";

        style.textContent = `
            .ats-clean-stats {
                max-width: 1260px;
                margin: 26px 0 34px;
                border: 1px solid rgba(201, 163, 58, 0.36);
                background:
                    linear-gradient(180deg, rgba(0,0,0,0.58), rgba(0,0,0,0.82)),
                    radial-gradient(circle at left top, rgba(201, 163, 58, 0.08), transparent 36%);
                padding: 22px;
                box-shadow: 0 0 26px rgba(0,0,0,0.34);
            }

            .ats-clean-stats h2 {
                margin: 0 0 8px;
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 34px;
                line-height: 1.12;
            }

            .ats-clean-stats__sub {
                color: #9f947f;
                line-height: 1.5;
                margin-bottom: 22px;
                max-width: 920px;
            }

            .ats-clean-stats__grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 14px;
                margin-bottom: 22px;
            }

            .ats-clean-card {
                border: 1px solid rgba(201, 163, 58, 0.28);
                background: rgba(255,255,255,0.035);
                padding: 16px;
                min-height: 108px;
            }

            .ats-clean-card__label {
                color: #bdb3a2;
                font-size: 13px;
                line-height: 1.3;
                margin-bottom: 8px;
            }

            .ats-clean-card__value {
                color: #f2d984;
                font-size: 34px;
                font-weight: 800;
                line-height: 1;
            }

            .ats-clean-card__hint {
                color: #766d5d;
                font-size: 12px;
                margin-top: 8px;
                line-height: 1.35;
            }

            .ats-clean-stats__meta {
                color: #9f947f;
                font-size: 13px;
                line-height: 1.5;
                padding: 12px 14px;
                border: 1px solid rgba(201, 163, 58, 0.18);
                background: rgba(0,0,0,0.28);
                margin-bottom: 18px;
            }

            .ats-clean-details {
                border: 1px solid rgba(201, 163, 58, 0.22);
                background: rgba(0,0,0,0.22);
                margin-top: 12px;
            }

            .ats-clean-details summary {
                cursor: pointer;
                padding: 13px 15px;
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 22px;
                user-select: none;
                list-style: none;
            }

            .ats-clean-details summary::-webkit-details-marker {
                display: none;
            }

            .ats-clean-details summary::before {
                content: "▸";
                display: inline-block;
                margin-right: 10px;
                color: #c9a33a;
            }

            .ats-clean-details[open] summary::before {
                transform: rotate(90deg);
            }

            .ats-clean-table {
                width: 100%;
                border-collapse: collapse;
                margin: 0;
            }

            .ats-clean-table th,
            .ats-clean-table td {
                padding: 10px 12px;
                border-top: 1px solid rgba(255,255,255,0.06);
                text-align: left;
                color: #e8dcc4;
                font-size: 14px;
            }

            .ats-clean-table th {
                color: #c9a33a;
                background: rgba(201, 163, 58, 0.08);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }

            .ats-clean-error {
                color: #ffb2a4;
                border: 1px solid rgba(192, 90, 74, 0.42);
                padding: 14px;
                background: rgba(192, 90, 74, 0.08);
            }

            @media (max-width: 1000px) {
                .ats-clean-stats__grid {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }

            @media (max-width: 640px) {
                .ats-clean-stats {
                    padding: 16px;
                }

                .ats-clean-stats__grid {
                    grid-template-columns: 1fr;
                }

                .ats-clean-stats h2 {
                    font-size: 28px;
                }
            }
        `;

        document.head.appendChild(style);
    }

    function n(value) {
        if (value === null || value === undefined) {
            return "—";
        }

        return String(value);
    }

    function table(title, rows, labelName) {
        var details = document.createElement("details");
        details.className = "ats-clean-details";

        if (title.indexOf("Топ") !== -1 || title.indexOf("Источники") !== -1) {
            details.open = true;
        }

        var summary = document.createElement("summary");
        summary.textContent = title;

        var html = '<table class="ats-clean-table"><thead><tr><th>' + labelName + '</th><th>Визиты</th></tr></thead><tbody>';

        if (!rows || !rows.length) {
            html += '<tr><td colspan="2">Нет данных</td></tr>';
        } else {
            rows.forEach(function (row) {
                html += '<tr><td>' + escapeHtml(row.label) + '</td><td>' + escapeHtml(row.count) + '</td></tr>';
            });
        }

        html += '</tbody></table>';

        details.appendChild(summary);
        details.insertAdjacentHTML("beforeend", html);

        return details;
    }

    function escapeHtml(value) {
        return String(value === null || value === undefined ? "" : value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function card(label, value, hint) {
        return `
            <div class="ats-clean-card">
                <div class="ats-clean-card__label">${escapeHtml(label)}</div>
                <div class="ats-clean-card__value">${escapeHtml(n(value))}</div>
                ${hint ? '<div class="ats-clean-card__hint">' + escapeHtml(hint) + '</div>' : ''}
            </div>
        `;
    }

    function mount(data) {
        var old = document.querySelector(".ats-clean-stats");
        if (old) {
            old.remove();
        }

        var h1 = Array.prototype.slice.call(document.querySelectorAll("h1"))
            .find(function (node) {
                return (node.textContent || "").toLowerCase().indexOf("статистика") !== -1;
            });

        if (!h1) {
            return;
        }

        var box = document.createElement("section");
        box.className = "ats-clean-stats";

        if (!data || !data.ok) {
            box.innerHTML = `
                <h2>Чистая статистика по людям</h2>
                <div class="ats-clean-error">
                    Не удалось собрать чистую статистику: ${escapeHtml(data && data.error ? data.error : "unknown error")}
                </div>
            `;
            h1.insertAdjacentElement("afterend", box);
            return;
        }

        var c = data.cards || {};
        var f = data.filters || {};
        var t = data.tables || {};

        box.innerHTML = `
            <h2>Чистая статистика по людям</h2>
            <div class="ats-clean-stats__sub">
                Это очищенный слой поверх сырой статистики: без админки, API, статики, сканеров, curl, ботов,
                WordPress-проб и технических обращений.
            </div>

            <div class="ats-clean-stats__grid">
                ${card("Чистые визиты сегодня", c.clean_today, "публичные страницы")}
                ${card("Чистые визиты за 7 дней", c.clean_7d, "после фильтрации")}
                ${card("Уникальные посетители за 7 дней", c.unique_7d, "по анонимному хэшу, если есть")}
                ${card("Просмотры формы за 7 дней", c.request_7d, "/request")}
                ${card("Реальные заявки за 7 дней", c.leads_7d, "из таблицы заявок")}
                ${card("Свободные эскизы за 7 дней", c.free_sketches_7d, "/categories/free-sketches")}
                ${card("Портфолио за 7 дней", c.projects_7d, "/projects и проекты")}
                ${card("Отсеяно мусора за 7 дней", f.excluded_7d, "боты, curl, api, админка")}
            </div>

            <div class="ats-clean-stats__meta">
                Сырых визитов за 7 дней: <strong>${escapeHtml(f.raw_7d)}</strong>.
                После очистки осталось: <strong>${escapeHtml(c.clean_7d)}</strong>.
                Это ближе к реальному интересу клиентов, но не является абсолютной аналитикой уровня Google Analytics.
            </div>
        `;

        box.appendChild(table("Топ чистых страниц за 7 дней", t.top_pages, "Страница"));
        box.appendChild(table("Источники чистых переходов", t.sources, "Источник"));
        box.appendChild(table("Устройства чистых визитов", t.devices, "Устройство"));
        box.appendChild(table("Браузеры чистых визитов", t.browsers, "Браузер"));

        h1.insertAdjacentElement("afterend", box);
    }

    function load() {
        addStyle();

        fetch(API_URL, {
            credentials: "same-origin",
            cache: "no-store",
            headers: {
                "Accept": "application/json"
            }
        })
            .then(function (response) {
                return response.json();
            })
            .then(mount)
            .catch(function (error) {
                mount({
                    ok: false,
                    error: String(error && error.message ? error.message : error)
                });
            });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", load);
    } else {
        load();
    }
})();
