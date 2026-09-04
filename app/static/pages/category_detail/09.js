(function () {
    "use strict";

    const pathname = window.location.pathname
        .replace(/\/+$/, "");

    if (pathname !== "/categories/paintings") {
        return;
    }

    function normalize(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim()
            .toUpperCase();
    }

    function cleanPaintingsPage() {

        /*
         * Удаляем старые секции «Примеры работ»,
         * кроме нового сгруппированного блока.
         */

        document
            .querySelectorAll("main section")
            .forEach(function (section) {
                if (
                    section.id ===
                    "atsPaintingsExamples"
                ) {
                    return;
                }

                if (
                    section.closest(
                        "#atsPaintingsExamples"
                    )
                ) {
                    return;
                }

                const headings = section.querySelectorAll(
                    "h1, h2, h3"
                );

                for (const heading of headings) {
                    if (
                        normalize(heading.textContent)
                        === "ПРИМЕРЫ РАБОТ"
                    ) {
                        section.remove();
                        return;
                    }
                }
            });

        /*
         * Удаляем старый общий проектный блок.
         */

        document
            .querySelectorAll(
                ".category-projects-section"
            )
            .forEach(function (section) {
                section.remove();
            });

        /*
         * Удаляем чужие карточки свободных эскизов,
         * если общий медиаскрипт вставит их позже.
         */

        document
            .querySelectorAll(
                ".japanese-free-sketch-card"
            )
            .forEach(function (card) {
                card.remove();
            });

        /*
         * На странице картин 3D-кнопки не нужны.
         */

        document
            .querySelectorAll(
                "a, button, [role='button']"
            )
            .forEach(function (element) {
                const label = normalize(
                    element.textContent
                );

                if (
                    label === "СМОТРЕТЬ 3D"
                    || label === "ПОСМОТРЕТЬ В 3D"
                ) {
                    element.remove();
                }
            });
    }

    cleanPaintingsPage();

    document.addEventListener(
        "DOMContentLoaded",
        cleanPaintingsPage
    );

    new MutationObserver(
        cleanPaintingsPage
    ).observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );
})();
