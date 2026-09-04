// ATS_LOGO_RELOAD_BUTTON_V3
        document.addEventListener('DOMContentLoaded', function () {
            const originalLogo =
                document.querySelector('header .logo.logo-image');

            if (!originalLogo) {
                return;
            }

            /*
             * Клонирование удаляет старые обработчики,
             * ранее назначенные непосредственно логотипу.
             */
            const logo = originalLogo.cloneNode(true);
            originalLogo.replaceWith(logo);

            const image = logo.querySelector('img');

            if (!image) {
                return;
            }

            let spinning = false;
            let touchTimer = 0;

            function enableGlow() {
                window.clearTimeout(touchTimer);
                logo.classList.add('ats-logo-touch');
            }

            function disableGlowLater() {
                window.clearTimeout(touchTimer);

                touchTimer = window.setTimeout(function () {
                    if (!spinning) {
                        logo.classList.remove('ats-logo-touch');
                    }
                }, 180);
            }

            function spinAndReload(event) {
                if (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    event.stopImmediatePropagation();
                }

                if (spinning) {
                    return;
                }

                spinning = true;
                logo.classList.add('ats-logo-spinning');
                logo.classList.add('ats-logo-touch');

                const duration = 620;
                const start = performance.now();

                function frame(now) {
                    const progress = Math.min(
                        (now - start) / duration,
                        1
                    );

                    /*
                     * Плавное замедление без увеличения,
                     * смещения и рывка в конце.
                     */
                    const eased =
                        1 - Math.pow(1 - progress, 3);

                    const angle = 360 * eased;

                    image.style.setProperty(
                        'transform',
                        'rotate(' + angle + 'deg)',
                        'important'
                    );

                    if (progress < 1) {
                        window.requestAnimationFrame(frame);
                        return;
                    }

                    image.style.setProperty(
                        'transform',
                        'rotate(360deg)',
                        'important'
                    );

                    window.setTimeout(function () {
                        window.location.reload();
                    }, 70);
                }

                window.requestAnimationFrame(frame);
            }

            logo.addEventListener(
                'pointerdown',
                enableGlow,
                { passive: true }
            );

            logo.addEventListener(
                'pointerup',
                disableGlowLater,
                { passive: true }
            );

            logo.addEventListener(
                'pointercancel',
                disableGlowLater,
                { passive: true }
            );

            logo.addEventListener(
                'pointerleave',
                disableGlowLater,
                { passive: true }
            );

            logo.addEventListener(
                'click',
                spinAndReload,
                true
            );

            logo.addEventListener(
                'keydown',
                function (event) {
                    if (
                        event.key === 'Enter' ||
                        event.key === ' '
                    ) {
                        spinAndReload(event);
                    }
                },
                true
            );
        });
