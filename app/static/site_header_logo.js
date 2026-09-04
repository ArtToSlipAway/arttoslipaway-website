/* ATS_HEADER_LOGO_EXACT_MOBILE_SCROLL_MOTION_V1 */

(function () {
    'use strict';

    function init() {

        /*
         * Правый логотип главной уже имеет
         * собственный оригинальный код.
         *
         * Здесь работаем только с логотипами
         * в header на остальных страницах.
         */
        if (window.location.pathname === '/') {
            return;
        }

        const logos = Array.from(
            document.querySelectorAll(
                'header a.ats-site-header-logo,' +
                'header a.logo.logo-image'
            )
        );

        logos.forEach(function (logo) {

            if (
                logo.dataset
                    .atsExactMotionReady ===
                'true'
            ) {
                return;
            }

            logo.dataset
                .atsExactMotionReady =
                'true';

            let reloadStarted = false;
            let touchTimer = null;

            function showTouchGlow() {

                window.clearTimeout(
                    touchTimer
                );

                logo.classList.add(
                    'is-touch'
                );

                touchTimer =
                    window.setTimeout(
                        function () {
                            logo.classList.remove(
                                'is-touch'
                            );
                        },
                        420
                    );
            }

            logo.addEventListener(
                'pointerdown',
                showTouchGlow,
                {
                    passive: true
                }
            );

            logo.addEventListener(
                'click',
                function (event) {

                    if (
                        event.metaKey ||
                        event.ctrlKey ||
                        event.shiftKey ||
                        event.altKey ||
                        event.button > 0
                    ) {
                        return;
                    }

                    event.preventDefault();
                    event.stopPropagation();
                    event.stopImmediatePropagation();

                    if (reloadStarted) {
                        return;
                    }

                    reloadStarted = true;

                    logo.classList.remove(
                        'is-spinning'
                    );

                    void logo.offsetWidth;

                    logo.classList.add(
                        'is-spinning'
                    );

                    window.setTimeout(
                        function () {

                            if (
                                window.location
                                    .pathname ===
                                '/'
                            ) {
                                window.location
                                    .reload();
                            } else {
                                window.location
                                    .href = '/';
                            }
                        },
                        620
                    );
                },
                true
            );
        });
    }

    if (
        document.readyState ===
        'loading'
    ) {
        document.addEventListener(
            'DOMContentLoaded',
            init,
            {
                once: true
            }
        );
    } else {
        init();
    }
})();
