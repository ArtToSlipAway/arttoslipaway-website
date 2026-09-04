(function () {
    const mutedIcon = `
        <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
            focusable="false"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
        >
            <path d="M11 5 6.8 8.4H3.5v7.2h3.3L11 19V5Z"></path>
            <path d="m16 9 5 5"></path>
            <path d="m21 9-5 5"></path>
        </svg>
    `;

    const soundIcon = `
        <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
            focusable="false"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
        >
            <path d="M11 5 6.8 8.4H3.5v7.2h3.3L11 19V5Z"></path>
            <path d="M15 9.2a4 4 0 0 1 0 5.6"></path>
            <path d="M18 6.5a7.5 7.5 0 0 1 0 11"></path>
        </svg>
    `;

    function initSoundIcon() {
        const video = document.getElementById("siteVideoBg");
        const button = document.getElementById("videoSoundToggle");

        if (!video || !button) {
            return;
        }

        function renderIcon() {
            const isMuted =
                video.muted ||
                video.volume === 0;

            button.innerHTML =
                isMuted
                    ? mutedIcon
                    : soundIcon;

            button.classList.toggle(
                "is-sound-on",
                !isMuted
            );

            const label =
                isMuted
                    ? "Включить звук"
                    : "Выключить звук";

            button.setAttribute("aria-label", label);
            button.setAttribute("title", label);
            button.setAttribute(
                "aria-pressed",
                isMuted ? "false" : "true"
            );
        }

        renderIcon();

        video.addEventListener(
            "volumechange",
            renderIcon
        );

        button.addEventListener(
            "click",
            function () {
                window.requestAnimationFrame(
                    renderIcon
                );
            }
        );
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initSoundIcon
        );
    } else {
        initSoundIcon();
    }
})();
