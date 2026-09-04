(function () {
    "use strict";

    if (!window.location.pathname.startsWith("/admin/stats")) {
        return;
    }

    function addStyle() {
        if (document.getElementById("atsStatsClarifyStyle")) {
            return;
        }

        var style = document.createElement("style");
        style.id = "atsStatsClarifyStyle";

        style.textContent = `
            .ats-stats-explainer {
                max-width: 1260px;
                margin: 22px 0 28px;
                border: 1px solid rgba(201, 163, 58, 0.30);
                background:
                    linear-gradient(180deg, rgba(0,0,0,0.48), rgba(0,0,0,0.72)),
                    radial-gradient(circle at left top, rgba(201, 163, 58, 0.07), transparent 34%);
                padding: 18px 20px;
                color: #cfc3ad;
                line-height: 1.55;
                font-size: 15px;
            }

            .ats-stats-explainer strong {
                color: #f2d984;
                font-weight: 700;
            }

            .ats-stats-explainer ul {
                margin: 10px 0 0;
                padding-left: 20px;
            }

            .ats-stats-explainer li {
                margin: 6px 0;
            }

            .ats-stats-note {
                margin-top: 12px;
                color: #9f947f;
                font-size: 13px;
            }

            .ats-stats-details {
                max-width: 1260px;
                margin: 18px 0;
                border: 1px solid rgba(201, 163, 58, 0.24);
                background: rgba(0,0,0,0.26);
            }

            .ats-stats-details[open] {
                background: rgba(0,0,0,0.38);
            }

            .ats-stats-details > summary {
                cursor: pointer;
                list-style: none;
                padding: 16px 18px;
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 24px;
                line-height: 1.2;
                border-bottom: 1px solid rgba(201, 163, 58, 0.18);
                user-select: none;
            }

            .ats-stats-details > summary::-webkit-details-marker {
                display: none;
            }

            .ats-stats-details > summary::before {
                content: "▸";
                display: inline-block;
                margin-right: 10px;
                color: #c9a33a;
                transition: transform 0.18s ease;
            }

            .ats-stats-details[open] > summary::before {
                transform: rotate(90deg);
            }

            .ats-stats-details__body {
                padding: 18px;
                overflow-x: auto;
            }

            .ats-stats-details__body h2,
            .ats-stats-details__body h3 {
                display: none !important;
            }

            .ats-stats-card-note {
                color: #9f947f;
                font-size: 13px;
                margin: -8px 0 22px;
                max-width: 980px;
                line-height: 1.45;
            }

            @media (max-width: 760px) {
                .ats-stats-explainer {
                    font-size: 14px;
                    padding: 15px;
                }

                .ats-stats-details > summary {
                    font-size: 20px;
                    padding: 14px;
                }

                .ats-stats-details__body {
                    padding: 14px;
                }
            }
        `;

        document.head.appendChild(style);
    }

    function replaceExactText(from, to) {
        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        var node;

        while ((node = walker.nextNode())) {
            if ((node.nodeValue || "").trim() === from) {
                node.nodeValue = node.nodeValue.replace(from, to);
            }
        }
    }

    function addExplainer() {
        if (document.querySelector(".ats-stats-explainer")) {
            return;
        }

        var h1 = Array.prototype.slice.call(document.querySelectorAll("h1"))
            .find(function (node) {
                return (node.textContent || "").toLowerCase().indexOf("статистика") !== -1;
            });

        if (!h1) {
            return;
        }

        var box = document.createElement("div");
        box.className = "ats-stats-explainer";

        box.innerHTML = `
            <strong>Как читать эти данные:</strong>
            <ul>
                <li><strong>Это локальная техническая статистика сайта</strong> из таблиц посещений и событий.</li>
                <li>В “сырые визиты” могут попадать реальные люди, поисковые и спам-боты, твои проверки сайта, запросы с сервера и технические страницы.</li>
                <li><strong>direct</strong> — пришли без источника перехода. <strong>internal</strong> — переход внутри сайта. Обращения с адреса сервера могут быть техническими проверками.</li>
                <li>Строки вроде <strong>/wp-login.php</strong> — это сканеры WordPress, не клиенты.</li>
                <li>Для оценки клиентов важнее смотреть: <strong>/request</strong>, <strong>/categories/free-sketches</strong>, заявки и клики по записи.</li>
            </ul>
            <div class="ats-stats-note">
                Следующий этап — разделить статистику на “люди”, “боты” и “технические проверки”, чтобы цифры были ближе к реальным посетителям.
            </div>
        `;

        var insertAfter = h1.nextElementSibling || h1;
        insertAfter.insertAdjacentElement("afterend", box);
    }

    function addCardNote() {
        if (document.querySelector(".ats-stats-card-note")) {
            return;
        }

        var firstTableHeading = Array.prototype.slice.call(document.querySelectorAll("h2, h3"))
            .find(function (node) {
                var text = (node.textContent || "").toLowerCase();
                return text.indexOf("топ страниц") !== -1 || text.indexOf("источники") !== -1;
            });

        if (!firstTableHeading) {
            return;
        }

        var note = document.createElement("div");
        note.className = "ats-stats-card-note";
        note.textContent = "Верхние карточки показывают сырую активность. Это не равно количеству клиентов и не равно уникальным людям.";

        firstTableHeading.insertAdjacentElement("beforebegin", note);
    }

    function makeSectionsCollapsible() {
        if (document.querySelector(".ats-stats-details")) {
            return;
        }

        var sectionTitles = [
            "Топ страниц за 7 дней",
            "Источники переходов за 7 дней",
            "Устройства",
            "Браузеры",
            "Последние визиты"
        ];

        var headings = Array.prototype.slice.call(document.querySelectorAll("h2, h3"))
            .filter(function (heading) {
                var title = (heading.textContent || "").trim();
                return sectionTitles.indexOf(title) !== -1;
            });

        headings.forEach(function (heading, index) {
            var title = (heading.textContent || "").trim();

            var details = document.createElement("details");
            details.className = "ats-stats-details";

            // Первые две секции оставляем открытыми, остальные экономят место.
            if (index < 2) {
                details.open = true;
            }

            var summary = document.createElement("summary");
            summary.textContent = title;

            var body = document.createElement("div");
            body.className = "ats-stats-details__body";

            heading.parentNode.insertBefore(details, heading);
            details.appendChild(summary);
            details.appendChild(body);

            var node = heading;
            while (node) {
                var next = node.nextSibling;

                if (
                    next &&
                    next.nodeType === 1 &&
                    ["H2", "H3"].indexOf(next.tagName) !== -1 &&
                    sectionTitles.indexOf((next.textContent || "").trim()) !== -1
                ) {
                    body.appendChild(node);
                    break;
                }

                body.appendChild(node);
                node = next;

                if (!node) {
                    break;
                }
            }
        });
    }

    function clarifyLabels() {
        replaceExactText("Визиты сегодня", "Сырые визиты сегодня");
        replaceExactText("Визиты за 7 дней", "Сырые визиты за 7 дней");
        replaceExactText("Форма заявки за 7 дней", "Просмотры формы за 7 дней");
        replaceExactText("Проекты за 7 дней", "Просмотры проектов за 7 дней");
        replaceExactText("Боты за 7 дней", "Боты и сканеры за 7 дней");
    }

    function run() {
        addStyle();
        clarifyLabels();
        addExplainer();
        addCardNote();
        makeSectionsCollapsible();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", run);
    } else {
        run();
    }
})();
