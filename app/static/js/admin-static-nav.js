(function () {
    "use strict";

    if (!window.location.pathname.startsWith("/admin")) {
        return;
    }

    if (window.location.pathname.startsWith("/admin/login")) {
        return;
    }

    var STYLE_ID = "atsAdminStaticNavStyle";
    var HEADER_SELECTOR = "[data-ats-static-admin-header]";

    var navItems = [
        { label: "Панель", href: "/admin", exact: true },
        { label: "Заявки", href: "/admin/leads" },
        { label: "Проекты", href: "/admin/projects" },
        { label: "Категории", href: "/admin/categories" },
        { label: "Даты", href: "/admin/city-slots" },
        { label: "Карусель", href: "/admin/carousel" },
        { label: "Медиа", href: "/admin/media" },
        { label: "Файлы", href: "/admin/upload-check" },
        { label: "Право", href: "/admin/legal" },
        { label: "Статистика", href: "/admin/stats" },
        { label: "Визуал", href: "/admin/visual" },
        { label: "Инфострока", href: "/admin/announcement" },
        { label: "Сервер", href: "/admin/system" },
        { label: "Выход", href: "/admin/logout" },
        { label: "Сайт", href: "/", external: true }
    ];

    function normalizePath(path) {
        path = String(path || "").replace(/\/+$/, "");

        if (!path) {
            return "/";
        }

        return path;
    }

    function isActive(item) {
        var current = normalizePath(window.location.pathname);
        var href = normalizePath(item.href);

        if (item.external) {
            return false;
        }

        if (item.exact) {
            return current === href;
        }

        return current === href || current.indexOf(href + "/") === 0;
    }

    function injectStyle() {
        if (document.getElementById(STYLE_ID)) {
            return;
        }

        var style = document.createElement("style");
        style.id = STYLE_ID;

        style.textContent = `
            [data-ats-static-admin-header] {
                max-width: 1360px;
                margin: 0 auto;
                padding: 28px 28px 0;
                box-sizing: border-box;
            }

            .admin-shell > [data-ats-static-admin-header] {
                max-width: none;
                padding: 0;
                margin: 0;
            }

            .ats-admin-static-brand {
                display: block;
                width: fit-content;
                color: #c9a33a !important;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 26px;
                line-height: 1.15;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                text-decoration: none !important;
                margin: 0 0 18px;
                white-space: nowrap;
            }

            .ats-admin-static-nav {
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
                margin: 0 0 44px;
                padding: 0;
            }

            .ats-admin-static-nav a {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                height: 36px;
                min-height: 36px;
                padding: 0 13px;
                border: 1px solid rgba(201, 163, 58, 0.28);
                color: #c9a33a !important;
                background: rgba(0,0,0,0.34);
                text-transform: uppercase;
                letter-spacing: 0.07em;
                font-size: 13px;
                line-height: 1;
                font-weight: 400;
                font-family: Arial, sans-serif;
                text-decoration: none !important;
                box-sizing: border-box;
                white-space: nowrap;
                transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
            }

            .ats-admin-static-nav a:hover,
            .ats-admin-static-nav a.is-active {
                background: #c9a33a;
                border-color: #c9a33a;
                color: #111 !important;
            }

            @media (max-width: 760px) {
                [data-ats-static-admin-header] {
                    padding: 22px 16px 0;
                }

                .admin-shell > [data-ats-static-admin-header] {
                    padding: 0;
                }

                .ats-admin-static-brand {
                    font-size: 22px;
                    letter-spacing: 0.12em;
                }

                .ats-admin-static-nav {
                    gap: 8px;
                    margin-bottom: 34px;
                }

                .ats-admin-static-nav a {
                    height: 34px;
                    min-height: 34px;
                    padding: 0 10px;
                    font-size: 12px;
                    letter-spacing: 0.055em;
                }
            }
        `;

        document.head.appendChild(style);
    }

    function buildHeader() {
        var header = document.createElement("div");
        header.setAttribute("data-ats-static-admin-header", "true");

        var brand = document.createElement("a");
        brand.className = "ats-admin-static-brand";
        brand.href = "/admin";
        brand.textContent = "ArtToSlipAway Admin";

        var nav = document.createElement("nav");
        nav.className = "ats-admin-static-nav";
        nav.setAttribute("aria-label", "Админ-навигация");

        navItems.forEach(function (item) {
            var link = document.createElement("a");
            link.href = item.href;
            link.textContent = item.label;

            if (item.external) {
                link.target = "_blank";
                link.rel = "noopener";
            }

            if (isActive(item)) {
                link.className = "is-active";
            }

            nav.appendChild(link);
        });

        header.appendChild(brand);
        header.appendChild(nav);

        return header;
    }

    function removeOldTopNavInsideShell(shell) {
        var directBrand = shell.querySelector(":scope > .admin-brand");
        var directNav = shell.querySelector(":scope > .admin-nav");

        if (directBrand) {
            directBrand.remove();
        }

        if (directNav) {
            directNav.remove();
        }
    }

    function mountHeader() {
        injectStyle();

        var oldStatic = document.querySelector(HEADER_SELECTOR);
        if (oldStatic) {
            oldStatic.remove();
        }

        var header = buildHeader();
        var shell = document.querySelector(".admin-shell");

        if (shell) {
            removeOldTopNavInsideShell(shell);

            /*
             * Shell-based pages must use the same page structure
             * as the dashboard:
             *
             * static header
             * content container
             *
             * Do not mount the header inside .admin-shell.
             */
            shell.parentNode.insertBefore(header, shell);
            return;
        }

        var oldHeader = document.querySelector("body > header") || document.querySelector("header");

        if (oldHeader) {
            oldHeader.replaceWith(header);
            return;
        }

        document.body.insertBefore(header, document.body.firstChild);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", mountHeader);
    } else {
        mountHeader();
    }
})();
