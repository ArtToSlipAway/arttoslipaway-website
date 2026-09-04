(function () {
    "use strict";

    function openModel(button) {
        const wrap = button.closest(
            ".japanese-free-sketch-card__viewer"
        );

        if (!wrap) {
            return;
        }

        const viewer = wrap.querySelector(
            "model-viewer"
        );

        if (!viewer) {
            return;
        }

        button.disabled = true;
        button.textContent = "Загрузка 3D…";

        /* ATS_VIEW_3D_AUTO_REVEAL_FIX_V1 */
        viewer.setAttribute(
            "loading",
            "eager"
        );

        viewer.setAttribute(
            "reveal",
            "auto"
        );

        viewer.setAttribute(
            "auto-rotate",
            ""
        );

        viewer.setAttribute(
            "auto-rotate-delay",
            "0"
        );

        function revealModel() {
            if (
                typeof viewer.dismissPoster
                === "function"
            ) {
                viewer.dismissPoster();
            } else {
                viewer.removeAttribute("poster");
            }

            wrap.classList.add("is-3d-open");
            button.remove();
        }

        if (viewer.loaded === true) {
            revealModel();
            return;
        }

        viewer.addEventListener(
            "load",
            revealModel,
            { once: true }
        );

        viewer.addEventListener(
            "error",
            function () {
                button.disabled = false;
                button.textContent =
                    "Повторить открытие 3D";
            },
            { once: true }
        );

        /*
         * Не перезапускаем src.
         * Смена loading на eager сама запускает загрузку.
         */
    }

    document.addEventListener(
        "click",
        function (event) {
            const button = event.target.closest(
                "[data-ats-view-3d]"
            );

            if (!button) {
                return;
            }

            event.preventDefault();
            event.stopPropagation();

            openModel(button);
        }
    );
})();
