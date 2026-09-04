(function () {
    const path = window.location.pathname;

    if (
        path.startsWith('/admin') ||
        path.startsWith('/request') ||
        path.startsWith('/thanks') ||
        path.startsWith('/static')
    ) {
        return;
    }

    function installStyles() {
        if (document.getElementById('projectCardsMediaStyles')) return;

        const style = document.createElement('style');
        style.id = 'projectCardsMediaStyles';

        style.textContent = `
            .project-card-media-cover {
                width: 100%;
                aspect-ratio: 1 / 0.72;
                margin: 0 0 14px;
                border: 1px solid rgba(201, 163, 58, 0.34);
                background: rgba(0,0,0,0.46);
                overflow: hidden;
                display: grid;
                place-items: center;
                color: rgba(232, 221, 198, 0.70);
                font-family: Arial, sans-serif;
                font-size: 13px;
                text-align: center;
                box-shadow:
                    0 0 18px rgba(0,0,0,0.32),
                    inset 0 0 18px rgba(201, 163, 58, 0.035);
            }

            .project-card-media-cover img,
            .project-card-media-cover video {
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
            }

            .project-card-media-cover video {
                background: #000;
            }

            .project-card-media-cover--model {
                padding: 14px;
                color: #c9a33a;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }

            .project-card-media-cover a {
                color: inherit;
                text-decoration: none;
                width: 100%;
                height: 100%;
                display: grid;
                place-items: center;
            }
        `;

        document.head.appendChild(style);
    }

    function getProjectSlugFromHref(href) {
        try {
            const url = new URL(href, window.location.origin);

            if (!url.pathname.startsWith('/projects/')) return '';
            if (url.pathname === '/projects/') return '';

            return decodeURIComponent(
                url.pathname.replace('/projects/', '').replace(/^\/+|\/+$/g, '')
            );
        } catch (error) {
            return '';
        }
    }

    function findCard(link) {
        return (
            link.closest('[data-project-card]') ||
            link.closest('article') ||
            link.closest('li') ||
            link.closest('.project-card') ||
            link.closest('.portfolio-card') ||
            link.closest('.work-card') ||
            link.closest('.card') ||
            link.closest('.project-item') ||
            link
        );
    }

    function createCover(media) {
        const cover = document.createElement('div');
        cover.className = 'project-card-media-cover';

        if (media.media_type === 'image') {
            const img = document.createElement('img');
            img.src = media.file_path;
            img.alt = media.alt_text || media.media_title || media.project_title || '';
            cover.appendChild(img);
            return cover;
        }

        if (media.media_type === 'video') {
            const video = document.createElement('video');
            video.muted = true;
            video.loop = true;
            video.playsInline = true;
            video.preload = 'metadata';

            if (media.poster_path) {
                video.poster = media.poster_path;
            }

            const source = document.createElement('source');
            source.src = media.file_path;

            video.appendChild(source);
            cover.appendChild(video);

            cover.addEventListener('mouseenter', function () {
                video.play().catch(function () {});
            });

            cover.addEventListener('mouseleave', function () {
                video.pause();
            });

            return cover;
        }

        if (media.media_type === 'model') {
            cover.classList.add('project-card-media-cover--model');

            if (media.poster_path) {
                const img = document.createElement('img');
                img.src = media.poster_path;
                img.alt = media.alt_text || media.media_title || '3D модель';
                cover.appendChild(img);
            } else {
                cover.textContent = '3D-модель';
            }

            return cover;
        }

        cover.textContent = 'Медиа';
        return cover;
    }

    function installCovers(covers) {
        if (!covers || typeof covers !== 'object') return;

        const links = Array.from(document.querySelectorAll('a[href*="/projects/"]'));

        links.forEach(function (link) {
            const slug = getProjectSlugFromHref(link.href);
            if (!slug) return;

            const media = covers[slug];
            if (!media) return;

            const card = findCard(link);
            if (!card || card.dataset.mediaCoverInstalled === '1') return;

            card.dataset.mediaCoverInstalled = '1';

            const cover = createCover(media);

            if (card === link) {
                card.insertBefore(cover, card.firstChild);
            } else {
                card.insertBefore(cover, card.firstChild);
            }
        });
    }

    fetch('/api/project-covers')
        .then(function (response) {
            if (!response.ok) throw new Error('covers api error');
            return response.json();
        })
        .then(function (covers) {
            installStyles();
            installCovers(covers);
        })
        .catch(function () {});
})();
