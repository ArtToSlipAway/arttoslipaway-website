(function () {
            const logo =
                document.getElementById(
                    'atsMobileScrollLogo'
                );

            if (!logo) {
                return;
            }

            const mobileMedia =
                window.matchMedia(
                    '(max-width: 768px)'
                );

            const START_SCROLL = 28;
            const END_SCROLL = 300;

            const MIN_WIDTH = 66;
            const MAX_WIDTH = 148;

            let frameRequested = false;
            let reloadStarted = false;
            let touchTimer = null;

            function clamp(value, minimum, maximum) {
                return Math.min(
                    maximum,
                    Math.max(minimum, value)
                );
            }

            function updateLogo() {
                frameRequested = false;

                if (!mobileMedia.matches) {
                    logo.style.opacity = '0';
                    logo.style.pointerEvents = 'none';
                    logo.setAttribute(
                        'aria-hidden',
                        'true'
                    );

                    return;
                }

                const scrollY =
                    window.scrollY ||
                    document.documentElement.scrollTop ||
                    0;

                const rawProgress =
                    (
                        scrollY -
                        START_SCROLL
                    ) /
                    (
                        END_SCROLL -
                        START_SCROLL
                    );

                const progress =
                    clamp(rawProgress, 0, 1);

                const easedProgress =
                    1 -
                    Math.pow(
                        1 - progress,
                        3
                    );

                const width =
                    MIN_WIDTH +
                    (
                        MAX_WIDTH -
                        MIN_WIDTH
                    ) *
                    easedProgress;

                const opacity =
                    progress <= 0
                        ? 0
                        : 0.18 +
                          0.54 *
                          easedProgress;

                const scale =
                    0.92 +
                    0.08 *
                    easedProgress;

                const translateY =
                    -6 +
                    6 *
                    easedProgress;

                const brightness =
                    0.42 +
                    0.34 *
                    easedProgress;

                const saturation =
                    0.70 +
                    0.12 *
                    easedProgress;

                const glowSize =
                    4 +
                    8 *
                    easedProgress;

                const glowOpacity =
                    0.08 +
                    0.14 *
                    easedProgress;

                logo.style.width =
                    width.toFixed(2) + 'px';

                logo.style.opacity =
                    opacity.toFixed(3);

                logo.style.transform =
                    'translate3d(-50%, ' +
                    translateY.toFixed(2) +
                    'px, 0) scale(' +
                    scale.toFixed(3) +
                    ')';

                logo.style.filter =
                    'brightness(' +
                    brightness.toFixed(3) +
                    ') saturate(' +
                    saturation.toFixed(3) +
                    ') drop-shadow(0 0 ' +
                    glowSize.toFixed(2) +
                    'px rgba(201, 163, 58, ' +
                    glowOpacity.toFixed(3) +
                    '))';

                const visible =
                    progress > 0.06;

                logo.style.pointerEvents =
                    visible
                        ? 'auto'
                        : 'none';

                logo.setAttribute(
                    'aria-hidden',
                    visible
                        ? 'false'
                        : 'true'
                );
            }

            function requestUpdate() {
                if (frameRequested) {
                    return;
                }

                frameRequested = true;

                window.requestAnimationFrame(
                    updateLogo
                );
            }

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
                    event.preventDefault();

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
                                window.location.pathname ===
                                '/'
                            ) {
                                window.location.reload();
                            } else {
                                window.location.href = '/';
                            }
                        },
                        620
                    );
                }
            );

            window.addEventListener(
                'scroll',
                requestUpdate,
                {
                    passive: true
                }
            );

            window.addEventListener(
                'resize',
                requestUpdate,
                {
                    passive: true
                }
            );

            window.addEventListener(
                'orientationchange',
                requestUpdate,
                {
                    passive: true
                }
            );

            mobileMedia.addEventListener?.(
                'change',
                requestUpdate
            );

            if (window.visualViewport) {
                window.visualViewport.addEventListener(
                    'resize',
                    requestUpdate,
                    {
                        passive: true
                    }
                );
            }

            requestUpdate();
        })();
