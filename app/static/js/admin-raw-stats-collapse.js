(function () {
    "use strict";

    if (!window.location.pathname.startsWith("/admin/stats")) {
        return;
    }

    var STYLE_ID = "atsRawStatsHardHideStyle";
    var BOX_CLASS = "ats-raw-stats-box";
    var HIDDEN_ATTR = "data-ats-raw-stats-hidden";

    function addStyle() {
        if (document.getElementById(STYLE_ID)) {
            return;
        }

        var style = document.createElement("style");
        style.id = STYLE_ID;

        style.textContent = `
            .ats-raw-stats-box {
                max-width: 1260px;
                margin: 34px 0 0;
                border: 1px solid rgba(201, 163, 58, 0.28);
                background: rgba(0,0,0,0.28);
            }

            .ats-raw-stats-box > summary {
                cursor: pointer;
                list-style: none;
                padding: 16px 18px;
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 26px;
                line-height: 1.2;
                user-select: none;
            }

            .ats-raw-stats-box > summary::-webkit-details-marker {
                display: none;
            }

            .ats-raw-stats-box > summary::before {
                content: "▸";
                display: inline-block;
                margin-right: 10px;
                color: #c9a33a;
                transition: transform 0.15s ease;
            }

            .ats-raw-stats-box[open] > summary::before {
                transform: rotate(90deg);
            }
        `;

        document.head.appendChild(style);
    }

    function ensureRawBox() {
        var cleanBox = document.querySelector(".ats-clean-stats");

        if (!cleanBox) {
            return null;
        }

        var boxes = Array.prototype.slice.call(document.querySelectorAll("." + BOX_CLASS));
        var box = boxes[0] || null;

        boxes.slice(1).forEach(function (extra) {
            extra.remove();
        });

        if (!box) {
            box = document.createElement("details");
            box.className = BOX_CLASS;

            var summary = document.createElement("summary");
            summary.textContent = "Сырая техническая статистика";

            box.appendChild(summary);
        }

        if (box.previousElementSibling !== cleanBox) {
            cleanBox.insertAdjacentElement("afterend", box);
        }

        return box;
    }

    function isSkippable(el, box) {
        if (!el || el === box || box.contains(el)) {
            return true;
        }

        if (el.tagName === "SCRIPT" || el.tagName === "STYLE") {
            return true;
        }

        if (el.id === STYLE_ID) {
            return true;
        }

        if (el.classList && el.classList.contains("ats-clean-stats")) {
            return true;
        }

        if (el.closest && el.closest(".ats-clean-stats")) {
            return true;
        }

        if (el.closest && el.closest("." + BOX_CLASS)) {
            return true;
        }

        return false;
    }

    function collectRawTopNodes(box) {
        var all = Array.prototype.slice.call(document.body.querySelectorAll("*"));

        var afterBox = all.filter(function (el) {
            if (isSkippable(el, box)) {
                return false;
            }

            return Boolean(box.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING);
        });

        var topNodes = [];

        afterBox.forEach(function (el) {
            var alreadyInside = topNodes.some(function (parent) {
                return parent.contains(el);
            });

            if (!alreadyInside) {
                topNodes.push(el);
            }
        });

        return topNodes;
    }

    function applyVisibility(box) {
        var rawNodes = collectRawTopNodes(box);

        rawNodes.forEach(function (el) {
            if (box.open) {
                el.style.removeProperty("display");
                el.removeAttribute(HIDDEN_ATTR);
            } else {
                el.style.setProperty("display", "none", "important");
                el.setAttribute(HIDDEN_ATTR, "1");
            }
        });
    }

    function init() {
        addStyle();

        var attempts = 0;
        var timer = setInterval(function () {
            attempts += 1;

            var box = ensureRawBox();

            if (box) {
                box.removeAttribute("open");
                applyVisibility(box);

                if (!box.dataset.atsRawStatsBound) {
                    box.dataset.atsRawStatsBound = "1";

                    box.addEventListener("toggle", function () {
                        applyVisibility(box);
                    });
                }

                setTimeout(function () {
                    applyVisibility(box);
                }, 300);

                setTimeout(function () {
                    applyVisibility(box);
                }, 900);

                setTimeout(function () {
                    applyVisibility(box);
                }, 1800);

                if (attempts > 8) {
                    clearInterval(timer);
                }
            }

            if (attempts > 50) {
                clearInterval(timer);
            }
        }, 150);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
