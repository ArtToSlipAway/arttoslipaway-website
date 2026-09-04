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
            video.play().catch(function () {
                button.textContent = 'Запустить фон';
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

        startVideo();
        updateButton();
    });
    // === /site video background ===
