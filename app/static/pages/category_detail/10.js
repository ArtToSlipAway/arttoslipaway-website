/* ATS_CERTIFICATE_PARTY_V6_JS */

(() => {

    const viewer =
        document.getElementById(
            "certificate-model-viewer"
        );

    if (!viewer) {
        return;
    }

    const shell =
        viewer.closest(
            ".certificate-model-shell"
        );

    if (!shell) {
        return;
    }

    let played = false;

    const colors = [
        "#d8ae3e",
        "#f1d77a",
        "#a77724",
        "#6e1f1d",
        "#214b36"
    ];


    /*
     * ATS_CERTIFICATE_TAP_CONFETTI_REPLAY_V1
     *
     * Обычный tap/click по сертификату:
     * повторить существующий launchParty().
     *
     * Drag для вращения модели:
     * ничего не запускать.
     *
     * Никакие pointer events не блокируем,
     * поэтому camera-controls продолжают
     * работать как раньше.
     */
    let certificatePartyPointer = null;

    const certificatePartyMoveLimit = (
        pointerType
    ) => {
        return pointerType === "touch"
            ? 12
            : 7;
    };

    viewer.addEventListener(
        "pointerdown",
        (event) => {

            if (!event.isPrimary) {
                return;
            }

            if (
                event.pointerType === "mouse"
                && event.button !== 0
            ) {
                return;
            }

            certificatePartyPointer = {
                id: event.pointerId,
                x: event.clientX,
                y: event.clientY,
                type: event.pointerType,
                moved: false
            };
        },
        true
    );

    viewer.addEventListener(
        "pointermove",
        (event) => {

            const state =
                certificatePartyPointer;

            if (
                !state
                || event.pointerId !== state.id
            ) {
                return;
            }

            const dx =
                event.clientX - state.x;

            const dy =
                event.clientY - state.y;

            const distance =
                Math.hypot(dx, dy);

            if (
                distance >
                certificatePartyMoveLimit(
                    state.type
                )
            ) {
                state.moved = true;
            }
        },
        true
    );

    viewer.addEventListener(
        "pointercancel",
        (event) => {

            if (
                certificatePartyPointer
                && event.pointerId ===
                    certificatePartyPointer.id
            ) {
                certificatePartyPointer = null;
            }
        },
        true
    );

    viewer.addEventListener(
        "pointerup",
        (event) => {

            const state =
                certificatePartyPointer;

            certificatePartyPointer = null;

            if (
                !state
                || event.pointerId !== state.id
            ) {
                return;
            }

            const dx =
                event.clientX - state.x;

            const dy =
                event.clientY - state.y;

            const distance =
                Math.hypot(dx, dy);

            const limit =
                certificatePartyMoveLimit(
                    state.type
                );

            if (
                state.moved
                || distance > limit
            ) {
                return;
            }

            /*
             * force=true снимает только
             * одноразовый played-lock.
             *
             * Вся существующая конфетти-
             * анимация используется без
             * изменений.
             */
            launchParty(true);
        },
        true
    );

    const launchParty = (force = false) => {

        if (played && !force) {
            return;
        }

        played = true;

        /*
         * Небольшая задержка:
         * браузер успевает отрисовать
         * первый кадр модели.
         */
        setTimeout(() => {

            shell.classList.add(
                "certificate-party-active"
            );

            const layer =
                document.createElement("div");

            layer.className =
                "ats-certificate-confetti";

            const count =
                window.innerWidth <= 820
                    ? 30
                    : 42;

            for (
                let i = 0;
                i < count;
                i += 1
            ) {

                const piece =
                    document.createElement("i");

                piece.className =
                    "ats-certificate-confetti-piece";

                const angle =
                    Math.random()
                    * Math.PI
                    * 2;

                const distanceX =
                    150
                    + Math.random()
                    * 360;

                const distanceY =
                    170
                    + Math.random()
                    * 390;

                const tx =
                    Math.cos(angle)
                    * distanceX;

                /*
                 * Больше частиц летит вверх,
                 * затем визуально осыпается.
                 */
                const ty =
                    -Math.abs(
                        Math.sin(angle)
                        * distanceY
                    )
                    - 80
                    + Math.random()
                    * 240;

                const width =
                    3
                    + Math.random()
                    * 6;

                const height =
                    width
                    * (
                        1.4
                        + Math.random()
                        * 1.5
                    );

                piece.style.setProperty(
                    "--tx",
                    `${tx.toFixed(0)}px`
                );

                piece.style.setProperty(
                    "--ty",
                    `${ty.toFixed(0)}px`
                );

                piece.style.setProperty(
                    "--rot",
                    `${
                        (
                            Math.random()
                            * 900
                            - 450
                        ).toFixed(0)
                    }deg`
                );

                piece.style.setProperty(
                    "--scale",
                    (
                        .55
                        + Math.random()
                        * .8
                    ).toFixed(2)
                );

                piece.style.setProperty(
                    "--delay",
                    `${
                        (
                            Math.random()
                            * .75
                        ).toFixed(2)
                    }s`
                );

                piece.style.setProperty(
                    "--duration",
                    `${
                        (
                            2.7
                            + Math.random()
                            * 1.1
                        ).toFixed(2)
                    }s`
                );

                piece.style.setProperty(
                    "--w",
                    `${width.toFixed(1)}px`
                );

                piece.style.setProperty(
                    "--h",
                    `${height.toFixed(1)}px`
                );

                piece.style.setProperty(
                    "--radius",
                    Math.random() > .72
                        ? "50%"
                        : "1px"
                );

                piece.style.setProperty(
                    "--color",
                    colors[
                        Math.floor(
                            Math.random()
                            * colors.length
                        )
                    ]
                );

                layer.appendChild(piece);
            }

            const isMobileParty =

                window.innerWidth <= 820;


            if (isMobileParty) {

                layer.classList.add(

                    "ats-certificate-confetti-mobile"

                );

                document.body.appendChild(layer);

            } else {

                shell.appendChild(layer);

            }
            setTimeout(() => {
                layer.remove();
            }, 4700);

        }, 100);
    };


    /*
     * ATS_CERTIFICATE_FAST_PARTY_V1
     *
     * Праздничная анимация не зависит от GLB.
     * Модель загружается параллельно в фоне.
     */
    const startPartyImmediately = () => {
        /* ATS_CERTIFICATE_EARLY_SHELL_V2 */
        shell.classList.add(
            "is-loaded",
            "certificate-party-active"
        );

        requestAnimationFrame(() => {
            launchParty();
        });
    };

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            startPartyImmediately,
            { once: true }
        );
    } else {
        startPartyImmediately();
    }

})();
