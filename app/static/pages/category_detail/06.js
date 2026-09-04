(function () {
    "use strict";

    const pathname = window.location.pathname
        .replace(/\/+$/, "");

    const supportedPages = new Set([
        "/categories/tattoo-engraving",
        "/categories/tattoo-traditional",
        "/categories/tattoo-dotwork"
    ]);

    if (!supportedPages.has(pathname)) {
        return;
    }

    document.documentElement.classList.add(
        "ats-other-tattoo-style-page"
    );

    function normalize(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim()
            .toUpperCase();
    }

    function cleanStylePage() {

        /*
         * Удаляем общий старый блок
         * «Примеры работ».
         */
        document
            .querySelectorAll("section")
            .forEach(function (section) {
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
         * Удаляем случайные внешние 3D-кнопки.
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
                    label !== "СМОТРЕТЬ 3D"
                    && label !== "ПОСМОТРЕТЬ В 3D"
                ) {
                    return;
                }

                if (
                    element.closest(
                        ".japanese-free-sketch-card"
                    )
                ) {
                    return;
                }

                element.remove();
            });

        /*
         * Удаляем японские карточки,
         * если общий медиаскрипт успел их вставить.
         */
        document
            .querySelectorAll(
                ".japanese-free-sketch-card"
            )
            .forEach(function (card) {
                const title = card.querySelector(
                    ".japanese-free-sketch-card__title"
                );

                const titleText = normalize(
                    title && title.textContent
                );

                if (
                    titleText === "КАРП"
                    || titleText === "МАКАЦУГЕ"
                ) {
                    card.remove();
                }
            });
    }

    cleanStylePage();

    document.addEventListener(
        "DOMContentLoaded",
        cleanStylePage
    );

    new MutationObserver(
        cleanStylePage
    ).observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );
})();
