(function () {
    "use strict";

    const pathname = window.location.pathname
        .replace(/\/+$/, "");

    if (
        pathname !==
        "/categories/tattoo-graphics"
    ) {
        return;
    }

    document.documentElement.classList.add(
        "ats-graphics-style-page"
    );

    function normalize(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim()
            .toUpperCase();
    }

    function removeForeignSections() {
        /*
         * Удаляем старый общий блок,
         * который подтягивал японские файлы.
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
         * Удаляем только случайные кнопки 3D,
         * не находящиеся внутри реальной карточки.
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
         * На графике пока не должно быть
         * японских карточек Карп/Макацуге.
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

    removeForeignSections();

    document.addEventListener(
        "DOMContentLoaded",
        removeForeignSections
    );

    new MutationObserver(
        removeForeignSections
    ).observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );
})();
