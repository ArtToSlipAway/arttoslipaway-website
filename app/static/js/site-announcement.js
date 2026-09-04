(function () {
    "use strict";

    var API_URL = "/api/announcement";
    var BAR_ID = "atsSiteAnnouncement";
    var STYLE_ID = "atsSiteAnnouncementStyle";

    function removeExisting() {
        var bar = document.getElementById(BAR_ID);
        var style = document.getElementById(STYLE_ID);

        if (bar) {
            bar.remove();
        }

        if (style) {
            style.remove();
        }
    }

    function clamp(value, fallback, min, max) {
        value = parseInt(value, 10);

        if (!Number.isFinite(value)) {
            value = fallback;
        }

        return Math.max(min, Math.min(max, value));
    }

    function group(text) {
        var g = document.createElement("div");
        g.className = "ats-site-announcement__group";

        for (var i = 0; i < 3; i += 1) {
            var item = document.createElement("span");
            item.className = "ats-site-announcement__item";
            item.textContent = text;

            var sep = document.createElement("span");
            sep.className = "ats-site-announcement__sep";
            sep.textContent = "◇";

            g.appendChild(item);
            g.appendChild(sep);
        }

        return g;
    }

    function render(config) {
        var enabled = Boolean(config && config.enabled);
        var text = String((config && config.text) || "").trim();

        if (!enabled || !text) {
            removeExisting();
            return;
        }

        var desktopSeconds = clamp(config.desktop_seconds, 85, 10, 240);
        var mobileSeconds = clamp(config.mobile_seconds, 75, 10, 240);

        removeExisting();

        var style = document.createElement("style");
        style.id = STYLE_ID;
        style.textContent = `
            .ats-site-announcement {
                width: 100%;
                margin: 0;
                padding: 0;
                position: sticky;
                top: 0;
                left: 0;
                z-index: 9999;
                background: #050505;
                overflow: hidden;
            }

            .ats-site-announcement__shell {
                width: 100%;
                overflow: hidden;
                border-bottom: 1px solid rgba(201, 163, 58, 0.72);
                background:
                    linear-gradient(90deg, rgba(0,0,0,0.98), rgba(22,16,6,0.95), rgba(0,0,0,0.98));
                box-shadow:
                    0 8px 28px rgba(0,0,0,0.45),
                    inset 0 0 20px rgba(201, 163, 58, 0.08);
                position: relative;
            }

            .ats-site-announcement__track {
                display: flex;
                width: max-content;
                animation: atsSiteAnnouncementScroll ${desktopSeconds}s linear infinite;
                will-change: transform;
                transform: translate3d(0, 0, 0);
            }

            .ats-site-announcement__group {
                display: flex;
                align-items: center;
                flex: 0 0 auto;
                white-space: nowrap;
            }

            .ats-site-announcement__item {
                display: inline-flex;
                align-items: center;
                padding: 10px 24px;
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 14px;
                letter-spacing: 0.03em;
                text-transform: none;
                text-shadow: 0 0 14px rgba(201, 163, 58, 0.36);
            }

            .ats-site-announcement__sep {
                display: inline-flex;
                align-items: center;
                color: #c9a33a;
                padding: 0 8px;
            }

            @keyframes atsSiteAnnouncementScroll {
                0% {
                    transform: translate3d(0, 0, 0);
                }
                100% {
                    transform: translate3d(-50%, 0, 0);
                }
            }

            .ats-site-announcement:hover .ats-site-announcement__track {
                animation-play-state: paused;
            }

            @media (max-width: 720px) {
                .ats-site-announcement__track {
                    animation-duration: ${mobileSeconds}s;
                }

                .ats-site-announcement__item {
                    font-size: 11px;
                    padding: 9px 18px;
                    letter-spacing: 0.02em;
                }
            }
        `;

        var bar = document.createElement("div");
        bar.id = BAR_ID;
        bar.className = "ats-site-announcement";

        var shell = document.createElement("div");
        shell.className = "ats-site-announcement__shell";

        var track = document.createElement("div");
        track.className = "ats-site-announcement__track";

        track.appendChild(group(text));

        var duplicate = group(text);
        duplicate.setAttribute("aria-hidden", "true");
        track.appendChild(duplicate);

        shell.appendChild(track);
        bar.appendChild(shell);

        document.head.appendChild(style);
        document.body.insertBefore(bar, document.body.firstChild);
    }

    function load() {
        fetch(API_URL, {
            credentials: "same-origin",
            cache: "no-store",
            headers: {
                "Accept": "application/json"
            }
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Announcement API failed");
                }

                return response.json();
            })
            .then(render)
            .catch(removeExisting);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", load);
    } else {
        load();
    }
})();
