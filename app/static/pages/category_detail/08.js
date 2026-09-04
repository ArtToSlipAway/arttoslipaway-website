(function () {
    "use strict";

    const pathname = window.location.pathname
        .replace(/\/+$/, "");

    if (pathname !== "/categories/tattoo") {
        return;
    }

    function normalize(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim()
            .toUpperCase();
    }

    function cleanTattooRootPage() {

        /*
         * Удаляем все старые секции
         * «Примеры работ», кроме нового блока.
         */

        document
            .querySelectorAll("main section")
            .forEach(function (section) {
                if (
                    section.id ===
                    "atsTattooRootExamples"
                ) {
                    return;
                }

                if (
                    section.closest(
                        "#atsTattooRootExamples"
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
         * Удаляем старый общий блок проектов,
         * даже если заголовок имеет другую разметку.
         */

        document
            .querySelectorAll(
                ".category-projects-section"
            )
            .forEach(function (section) {
                section.remove();
            });

        /*
         * На корневой странице татуировки
         * не должно быть никаких 3D-кнопок.
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

        /*
         * Удаляем чужие карточки свободных эскизов,
         * если старый медиаскрипт успел их вставить.
         */

        document
            .querySelectorAll(
                ".japanese-free-sketch-card"
            )
            .forEach(function (card) {
                card.remove();
            });
    }

    cleanTattooRootPage();

    document.addEventListener(
        "DOMContentLoaded",
        cleanTattooRootPage
    );

    new MutationObserver(
        cleanTattooRootPage
    ).observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );
})();
