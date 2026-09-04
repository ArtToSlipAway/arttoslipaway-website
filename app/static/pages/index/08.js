(function () {
            'use strict';

            function initLogoSpin() {
                const logoLink =
                    document.querySelector(
                        'header .logo.logo-image'
                    );

                if (!logoLink) {
                    return;
                }

                const logoImage =
                    logoLink.querySelector('img');

                if (!logoImage) {
                    return;
                }

                if (
                    logoLink.dataset.cleanSpinReady ===
                    'true'
                ) {
                    return;
                }

                logoLink.dataset.cleanSpinReady = 'true';

                let spinning = false;
                let fallbackTimer = null;

                function completeSpin(destination) {
                    if (!spinning) {
                        return;
                    }

                    spinning = false;

                    logoLink.classList.remove(
                        'is-spinning'
                    );

                    if (fallbackTimer) {
                        window.clearTimeout(
                            fallbackTimer
                        );

                        fallbackTimer = null;
                    }

                    if (destination) {
                        window.location.assign(
                            destination
                        );
                    }
                }

                logoLink.addEventListener(
                    'click',
                    function (event) {
                        if (
                            event.defaultPrevented ||
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

                        if (spinning) {
                            return;
                        }

                        spinning = true;

                        logoLink.classList.remove(
                            'is-spinning'
                        );

                        void logoImage.offsetWidth;

                        logoLink.classList.add(
                            'is-spinning'
                        );

                        const target =
                            new URL(
                                logoLink.href,
                                window.location.href
                            );

                        const current =
                            new URL(
                                window.location.href
                            );

                        const sameLocation =
                            target.origin === current.origin &&
                            target.pathname === current.pathname &&
                            target.search === current.search &&
                            target.hash === current.hash;

                        const destination =
                            sameLocation
                                ? ''
                                : target.href;

                        logoImage.addEventListener(
                            'animationend',
                            function onAnimationEnd(event) {
                                if (
                                    event.animationName !==
                                    'atsLogoCleanSpinV2'
                                ) {
                                    return;
                                }

                                completeSpin(destination);
                            },
                            {
                                once: true
                            }
                        );

                        fallbackTimer =
                            window.setTimeout(
                                function () {
                                    completeSpin(
                                        destination
                                    );
                                },
                                850
                            );
                    },
                    true
                );
            }

            if (
                document.readyState ===
                'loading'
            ) {
                document.addEventListener(
                    'DOMContentLoaded',
                    initLogoSpin,
                    {
                        once: true
                    }
                );
            } else {
                initLogoSpin();
            }
        })();
