// === site video background ===
    document.addEventListener('DOMContentLoaded', function () {
        const video = document.getElementById('siteVideoBg');
        const button = document.getElementById('videoSoundToggle');

        if (!video || !button) return;

        let soundEnabled = false;

        video.loop = true;
        video.muted = true;
        video.volume = 0.42;

        document.body.classList.remove('video-bg-frozen');
        document.body.classList.remove('eyes-active');

        function updateButton() {
            if (soundEnabled) {
                button.textContent = 'Выключить звук';
                button.classList.add('is-on');
            } else {
                button.textContent = 'Включить звук';
                button.classList.remove('is-on');
            }
        }

        function startVideo() {
            return video.play().catch(function () {
                button.setAttribute('aria-label', 'Запустить фон');
                button.setAttribute('title', 'Запустить фон');
            });
        }

        button.addEventListener('click', function () {
            if (video.paused) {
                startVideo();
            }

            soundEnabled = !soundEnabled;
            video.muted = !soundEnabled;

            if (soundEnabled) {
                video.volume = 0.42;
            }

            updateButton();
        });

        const connection =
            navigator.connection ||
            navigator.mozConnection ||
            navigator.webkitConnection;

        const prefersReducedMotion = window.matchMedia(
            '(prefers-reduced-motion: reduce)'
        ).matches;

        const constrainedConnection = Boolean(
            connection && (
                connection.saveData ||
                /(^|-)2g$/.test(connection.effectiveType || '')
            )
        );

        if (prefersReducedMotion || constrainedConnection) {
            video.preload = 'none';
        } else {
            const schedulePlayback = function () {
                if ('requestIdleCallback' in window) {
                    window.requestIdleCallback(startVideo, { timeout: 1200 });
                } else {
                    window.setTimeout(startVideo, 250);
                }
            };

            if (document.readyState === 'complete') {
                schedulePlayback();
            } else {
                window.addEventListener('load', schedulePlayback, { once: true });
            }
        }

        document.addEventListener('visibilitychange', function () {
            if (document.hidden) {
                video.pause();
            } else if (!prefersReducedMotion && !constrainedConnection) {
                startVideo();
            }
        });

        updateButton();
    });
    // === /site video background ===
