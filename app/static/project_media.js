(function () {
    const path = window.location.pathname;

    if (!path.startsWith('/projects/') || path === '/projects/') {
        return;
    }

    const slug = decodeURIComponent(path.replace('/projects/', '').replace(/^\/+|\/+$/g, ''));

    if (!slug) return;

    function installStyles() {
        if (document.getElementById('projectMediaStyles')) return;

        const style = document.createElement('style');
        style.id = 'projectMediaStyles';

        style.textContent = `
            .project-media-section {
                position: relative;
                z-index: 2;
                max-width: 1180px;
                margin: 46px auto 80px;
                padding: 0 24px;
            }

            .project-media-title {
                color: #c9a33a;
                font-family: Georgia, "Times New Roman", serif;
                font-size: clamp(32px, 4vw, 58px);
                line-height: 1;
                font-weight: 400;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin: 0 0 26px;
                text-shadow: 0 0 18px rgba(201, 163, 58, 0.12);
            }

            .project-media-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 18px;
            }

            .project-media-card {
                border: 1px solid rgba(201, 163, 58, 0.34);
                background:
                    linear-gradient(180deg, rgba(0,0,0,0.52), rgba(0,0,0,0.84)),
                    radial-gradient(circle at left top, rgba(201, 163, 58, 0.06), transparent 36%);
                padding: 14px;
                box-shadow: 0 0 24px rgba(0,0,0,0.34);
            }

            .project-media-preview {
                width: 100%;
                aspect-ratio: 1 / 0.72;
                border: 1px solid rgba(201, 163, 58, 0.20);
                background: rgba(0,0,0,0.46);
                overflow: hidden;
                display: grid;
                place-items: center;
                color: rgba(232, 221, 198, 0.72);
                text-align: center;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }

            .project-media-preview img,
            .project-media-preview video {
                display: block;
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .project-media-preview video {
                background: #000;
            }

            .project-media-info {
                padding-top: 12px;
            }

            .project-media-name {
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 20px;
                line-height: 1.2;
                margin-bottom: 6px;
            }

            .project-media-meta {
                color: rgba(232, 221, 198, 0.58);
                font-family: Arial, sans-serif;
                font-size: 13px;
                line-height: 1.4;
            }

            .project-media-link {
                display: inline-flex;
                margin-top: 10px;
                border: 1px solid rgba(201, 163, 58, 0.46);
                color: #c9a33a;
                padding: 8px 10px;
                text-decoration: none;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                font-size: 12px;
            }

            .project-media-link:hover {
                color: #111;
                background: #f2d984;
                border-color: #f2d984;
            }

            @media (max-width: 1000px) {
                .project-media-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }

            @media (max-width: 640px) {
                .project-media-grid {
                    grid-template-columns: 1fr;
                }

                .project-media-section {
                    padding: 0 16px;
                }
            }
        `;

        document.head.appendChild(style);
    }

    function mediaTypeLabel(type) {
        if (type === 'image') return 'Изображение';
        if (type === 'video') return 'Видео';
        if (type === 'model') return '3D-модель';
        return 'Файл';
    }

    function createCard(file) {
        const card = document.createElement('article');
        card.className = 'project-media-card';

        const preview = document.createElement('div');
        preview.className = 'project-media-preview';

        if (file.media_type === 'image') {
            const link = document.createElement('a');
            link.href = file.file_path;
            link.target = '_blank';

            const img = document.createElement('img');
            img.src = file.file_path;
            img.alt = file.alt_text || file.title || '';

            link.appendChild(img);
            preview.appendChild(link);
        } else if (file.media_type === 'video') {
            const video = document.createElement('video');
            video.controls = true;
            video.preload = 'metadata';
            video.playsInline = true;

            if (file.poster_path) {
                video.poster = file.poster_path;
            }

            const source = document.createElement('source');
            source.src = file.file_path;

            video.appendChild(source);
            preview.appendChild(video);
        } else if (file.media_type === 'model') {
            if (file.poster_path) {
                const link = document.createElement('a');
                link.href = file.file_path;
                link.target = '_blank';

                const img = document.createElement('img');
                img.src = file.poster_path;
                img.alt = file.alt_text || file.title || '3D-модель';

                link.appendChild(img);
                preview.appendChild(link);
            } else {
                const link = document.createElement('a');
                link.href = file.file_path;
                link.target = '_blank';
                link.className = 'project-media-link';
                link.textContent = 'Открыть 3D-модель';
                preview.appendChild(link);
            }
        } else {
            const link = document.createElement('a');
            link.href = file.file_path;
            link.target = '_blank';
            link.className = 'project-media-link';
            link.textContent = 'Открыть файл';
            preview.appendChild(link);
        }

        const info = document.createElement('div');
        info.className = 'project-media-info';

        const name = document.createElement('div');
        name.className = 'project-media-name';
        name.textContent = file.title || file.original_filename || mediaTypeLabel(file.media_type);

        const meta = document.createElement('div');
        meta.className = 'project-media-meta';
        meta.textContent = mediaTypeLabel(file.media_type);

        info.appendChild(name);
        info.appendChild(meta);

        if (file.media_type === 'model') {
            const link = document.createElement('a');
            link.href = file.file_path;
            link.target = '_blank';
            link.className = 'project-media-link';
            link.textContent = 'Открыть / скачать 3D';
            info.appendChild(link);
        }

        card.appendChild(preview);
        card.appendChild(info);

        return card;
    }

    function render(media) {
        if (!media || !media.length) return;

        installStyles();

        if (document.querySelector('.project-media-section')) return;

        const section = document.createElement('section');
        section.className = 'project-media-section';

        const title = document.createElement('h2');
        title.className = 'project-media-title';
        title.textContent = 'Медиа проекта';

        const grid = document.createElement('div');
        grid.className = 'project-media-grid';

        media.forEach(function (file) {
            grid.appendChild(createCard(file));
        });

        section.appendChild(title);
        section.appendChild(grid);

        const main = document.querySelector('main');

        if (main) {
            main.appendChild(section);
        } else {
            document.body.appendChild(section);
        }
    }

    fetch('/api/project-media/' + encodeURIComponent(slug))
        .then(function (response) {
            if (!response.ok) throw new Error('media api error');
            return response.json();
        })
        .then(function (data) {
            render(data.media || []);
        })
        .catch(function () {});
})();
