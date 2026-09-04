(function () {
            'use strict';

            function initInteractiveLogoGlow() {
                const logo =
                    document.querySelector(
                        'header .logo.logo-image'
                    );

                if (
                    !logo ||
                    logo.dataset.interactiveGlowReady ===
                        'true'
                ) {
                    return;
                }

                logo.dataset.interactiveGlowReady =
                    'true';

                let releaseTimer = null;

                function enableGlow() {
                    if (releaseTimer) {
                        window.clearTimeout(
                            releaseTimer
                        );

                        releaseTimer = null;
                    }

                    logo.classList.add(
                        'is-glow-active'
                    );
                }

                function disableGlow() {
                    if (
                        logo.classList.contains(
                            'is-spinning'
                        )
                    ) {
                        return;
                    }

                    logo.classList.remove(
                        'is-glow-active'
                    );
                }

                function scheduleDisableGlow() {
                    if (releaseTimer) {
                        window.clearTimeout(
                            releaseTimer
                        );
                    }

                    releaseTimer =
                        window.setTimeout(
                            disableGlow,
                            140
                        );
                }

                logo.addEventListener(
                    'pointerdown',
                    enableGlow,
                    {
                        passive: true
                    }
                );

                logo.addEventListener(
                    'pointerup',
                    scheduleDisableGlow,
                    {
                        passive: true
                    }
                );

                logo.addEventListener(
                    'pointercancel',
                    scheduleDisableGlow,
                    {
                        passive: true
                    }
                );

                logo.addEventListener(
                    'animationend',
                    function () {
                        logo.classList.remove(
                            'is-glow-active'
                        );
                    }
                );

                logo.addEventListener(
                    'blur',
                    disableGlow
                );
            }

            if (
                document.readyState ===
                'loading'
            ) {
                document.addEventListener(
                    'DOMContentLoaded',
                    initInteractiveLogoGlow,
                    {
                        once: true
                    }
                );
            } else {
                initInteractiveLogoGlow();
            }
        })();
