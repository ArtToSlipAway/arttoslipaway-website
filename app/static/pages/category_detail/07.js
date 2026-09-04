(function () {
    "use strict";

    const pathname = window.location.pathname
        .replace(/\/+$/, "");

    if (pathname !== "/categories/merch") {
        return;
    }

    document.documentElement.classList.add(
        "ats-merch-page"
    );

    function normalize(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim()
            .toUpperCase();
    }

    function cleanMerchPage() {
        /*
         * Удаляем прежние общие разделы,
         * которые не относятся к мерчу.
         */
        document
            .querySelectorAll("main section")
            .forEach(function (section) {
                if (
                    section.id === "atsMerchCatalog"
                    || section.closest("#atsMerchCatalog")
                ) {
                    return;
                }

                const headings = section.querySelectorAll(
                    "h1, h2, h3"
                );

                for (const heading of headings) {
                    const title = normalize(
                        heading.textContent
                    );

                    if (
                        title === "ПРИМЕРЫ РАБОТ"
                        || title === "ВЫПОЛНЕННЫЕ ПРОЕКТЫ"
                        || title === "СВОБОДНЫЕ ЭСКИЗЫ"
                    ) {
                        section.remove();
                        return;
                    }
                }
            });

        /*
         * Удаляем чужие японские карточки,
         * если общий медиаскрипт вставил их позже.
         */
        document
            .querySelectorAll(
                ".japanese-free-sketch-card"
            )
            .forEach(function (card) {
                card.remove();
            });

        /*
         * Удаляем случайные кнопки просмотра 3D.
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

    cleanMerchPage();

    document.addEventListener(
        "DOMContentLoaded",
        cleanMerchPage
    );

    new MutationObserver(
        cleanMerchPage
    ).observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );
})();
