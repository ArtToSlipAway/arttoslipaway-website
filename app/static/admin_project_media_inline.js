(function () {
    const match = window.location.pathname.match(/^\/admin\/projects\/(\d+)\/edit\/?$/);

    if (!match) return;

    const projectId = match[1];

    function installStyles() {
        if (document.getElementById('adminProjectMediaInlineStyles')) return;

        const style = document.createElement('style');
        style.id = 'adminProjectMediaInlineStyles';

        style.textContent = `
            .inline-media-panel {
                max-width: 1280px;
                margin: 28px auto 70px;
                padding: 22px;
                border: 1px solid rgba(201, 163, 58, 0.34);
                background:
                    linear-gradient(180deg, rgba(0,0,0,0.58), rgba(0,0,0,0.84)),
                    radial-gradient(circle at left top, rgba(201, 163, 58, 0.06), transparent 36%);
                color: #e8ddc6;
                font-family: Arial, sans-serif;
            }

            .inline-media-title {
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 30px;
                font-weight: 400;
                margin: 0 0 14px;
            }

            .inline-media-hint {
                color: #9f947c;
                line-height: 1.5;
                margin-bottom: 20px;
            }

            .inline-media-form {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 12px;
                margin-bottom: 26px;
            }

            .inline-media-field {
                display: flex;
                flex-direction: column;
                gap: 7px;
            }

            .inline-media-field.full {
                grid-column: 1 / -1;
            }

            .inline-media-field label {
                color: #c9a33a;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .inline-media-field input,
            .inline-media-field select,
            .inline-media-field textarea,
            .inline-media-field button,
            .inline-media-card input,
            .inline-media-card select,
            .inline-media-card textarea,
            .inline-media-card button {
                width: 100%;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }

            .inline-media-field input,
            .inline-media-field select,
            .inline-media-field textarea,
            .inline-media-card input,
            .inline-media-card select,
            .inline-media-card textarea {
                border: 1px solid rgba(201, 163, 58, 0.32);
                background: rgba(0,0,0,0.56);
                color: #e8ddc6;
                padding: 10px;
                outline: none;
            }

            .inline-media-field textarea,
            .inline-media-card textarea {
                min-height: 68px;
                resize: vertical;
            }

            .inline-media-field button,
            .inline-media-card button {
                border: 1px solid #c9a33a;
                background: #c9a33a;
                color: #111;
                padding: 11px 12px;
                text-transform: uppercase;
                letter-spacing: 0.07em;
                cursor: pointer;
            }

            .inline-media-field button:hover,
            .inline-media-card button:hover {
                background: #f2d984;
                border-color: #f2d984;
            }

            .inline-media-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
            }

            .inline-media-card {
                border: 1px solid rgba(201, 163, 58, 0.22);
                background: rgba(0,0,0,0.34);
                padding: 14px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .inline-media-preview {
                width: 100%;
                aspect-ratio: 1 / 0.7;
                background: rgba(0,0,0,0.46);
                border: 1px solid rgba(201, 163, 58, 0.18);
                overflow: hidden;
                display: grid;
                place-items: center;
                color: rgba(232,221,198,0.70);
                text-align: center;
                font-size: 13px;
            }

            .inline-media-preview img,
            .inline-media-preview video {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .inline-media-actions {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }

            .inline-media-danger {
                border-color: #c05a4a !important;
                background: transparent !important;
                color: #c05a4a !important;
            }

            .inline-media-danger:hover {
                background: #c05a4a !important;
                color: #111 !important;
            }

            .inline-media-status {
                color: #9f947c;
                font-size: 13px;
                line-height: 1.4;
            }

            @media (max-width: 1000px) {
                .inline-media-form,
                .inline-media-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }

            @media (max-width: 680px) {
                .inline-media-form,
                .inline-media-grid,
                .inline-media-actions {
                    grid-template-columns: 1fr;
                }
            }
        `;

        document.head.appendChild(style);
    }

    function blockLabel(value) {
        const labels = {
            project_gallery: 'Галерея проекта',
            portfolio_gallery: 'Портфолио',
            free_sketch_gallery: 'Свободный эскиз',
            project_process: 'Процесс',
            project_3d: '3D-блок'
        };

        return labels[value] || value || '—';
    }

    function createPreview(file) {
        const preview = document.createElement('div');
        preview.className = 'inline-media-preview';

        if (file.media_type === 'image') {
            const img = document.createElement('img');
            img.src = file.file_path;
            img.alt = file.alt_text || file.title || '';
            preview.appendChild(img);
            return preview;
        }

        if (file.media_type === 'video') {
            const video = document.createElement('video');
            video.controls = true;
            video.muted = true;
            video.preload = 'metadata';

            if (file.poster_path) video.poster = file.poster_path;

            const source = document.createElement('source');
            source.src = file.file_path;

            video.appendChild(source);
            preview.appendChild(video);
            return preview;
        }

        if (file.media_type === 'model') {
            if (file.poster_path) {
                const img = document.createElement('img');
                img.src = file.poster_path;
                preview.appendChild(img);
            } else {
                const link = document.createElement('a');
                link.href = file.file_path;
                link.target = '_blank';
                link.textContent = 'Открыть 3D-модель';
                preview.appendChild(link);
            }

            return preview;
        }

        preview.textContent = 'Файл';
        return preview;
    }

    function createMediaCard(file) {
        const card = document.createElement('article');
        card.className = 'inline-media-card';

        card.appendChild(createPreview(file));

        const status = document.createElement('div');
        status.className = 'inline-media-status';
        status.innerHTML = `
            <strong>${file.title || file.original_filename || 'Файл #' + file.id}</strong><br>
            Тип: ${file.media_type}<br>
            Блок: ${blockLabel(file.block_key)}<br>
            Статус: ${file.is_active ? 'показывается' : 'скрыт'}<br>
            Путь: <a href="${file.file_path}" target="_blank">${file.file_path}</a>
        `;
        card.appendChild(status);

        const editForm = document.createElement('form');
        editForm.action = `/admin/projects/${projectId}/media/${file.id}/edit`;
        editForm.method = 'post';
        editForm.innerHTML = `
            <div class="inline-media-field">
                <label>Название</label>
                <input name="title" value="${(file.title || '').replace(/"/g, '&quot;')}">
            </div>

            <div class="inline-media-field">
                <label>Блок</label>
                <select name="block_key">
                    <option value="project_gallery" ${file.block_key === 'project_gallery' ? 'selected' : ''}>Галерея проекта</option>
                    <option value="portfolio_gallery" ${file.block_key === 'portfolio_gallery' ? 'selected' : ''}>Портфолио</option>
                    <option value="free_sketch_gallery" ${file.block_key === 'free_sketch_gallery' ? 'selected' : ''}>Свободный эскиз</option>
                    <option value="project_process" ${file.block_key === 'project_process' ? 'selected' : ''}>Процесс</option>
                    <option value="project_3d" ${file.block_key === 'project_3d' ? 'selected' : ''}>3D-блок</option>
                </select>
            </div>

            <div class="inline-media-field">
                <label>Порядок показа</label>
                <input name="sort_order" type="number" value="${file.sort_order || 100}">
            </div>

            <div class="inline-media-field">
                <label>Описание</label>
                <textarea name="alt_text">${file.alt_text || ''}</textarea>
            </div>

            <button type="submit">Сохранить</button>
        `;
        card.appendChild(editForm);

        const actions = document.createElement('div');
        actions.className = 'inline-media-actions';

        const toggleForm = document.createElement('form');
        toggleForm.action = `/admin/projects/${projectId}/media/${file.id}/toggle`;
        toggleForm.method = 'post';
        toggleForm.innerHTML = `<button type="submit">${file.is_active ? 'Скрыть' : 'Показать'}</button>`;

        const deleteForm = document.createElement('form');
        deleteForm.action = `/admin/projects/${projectId}/media/${file.id}/delete`;
        deleteForm.method = 'post';
        deleteForm.onsubmit = function () {
            return confirm('Удалить медиафайл из проекта и с сервера?');
        };
        deleteForm.innerHTML = `<button class="inline-media-danger" type="submit">Удалить</button>`;

        actions.appendChild(toggleForm);
        actions.appendChild(deleteForm);

        card.appendChild(actions);

        return card;
    }

    function render(data) {
        installStyles();

        if (document.querySelector('.inline-media-panel')) return;

        const panel = document.createElement('section');
        panel.className = 'inline-media-panel';

        panel.innerHTML = `
            <h2 class="inline-media-title">Медиа проекта</h2>
            <div class="inline-media-hint">
                Здесь можно загрузить картинки, видео и 3D-модели прямо в этот проект.
                Эти файлы будут использоваться на странице проекта, в карточках и в будущих блоках портфолио.
            </div>

            <form class="inline-media-form" action="/admin/projects/${projectId}/media/upload" method="post" enctype="multipart/form-data">
                <div class="inline-media-field">
                    <label>Тип файла</label>
                    <select name="media_type">
                        <option value="auto">Определить автоматически</option>
                        <option value="image">Картинка</option>
                        <option value="video">Видео</option>
                        <option value="model">3D-модель</option>
                    </select>
                </div>

                <div class="inline-media-field">
                    <label>Тип проекта</label>
                    <select name="media_owner_type">
                        <option value="auto">Автоматически</option>
                        <option value="project">Проект</option>
                        <option value="portfolio">Портфолио</option>
                        <option value="free_sketch">Свободный эскиз</option>
                    </select>
                </div>

                <div class="inline-media-field">
                    <label>Блок</label>
                    <select name="block_key">
                        <option value="project_gallery">Галерея проекта</option>
                        <option value="portfolio_gallery">Портфолио</option>
                        <option value="free_sketch_gallery">Свободный эскиз</option>
                        <option value="project_process">Процесс</option>
                        <option value="project_3d">3D-блок</option>
                    </select>
                </div>

                <div class="inline-media-field">
                    <label>Порядок показа</label>
                    <input name="sort_order" type="number" value="100">
                </div>

                <div class="inline-media-field">
                    <label>Название</label>
                    <input name="title" placeholder="Например: видео процесса / 3D-модель">
                </div>

                <div class="inline-media-field">
                    <label>Файл</label>
                    <input name="file" type="file" required accept=".jpg,.jpeg,.png,.webp,.gif,.mp4,.webm,.mov,.glb,.gltf,.obj,.stl,.usdz">
                </div>

                <div class="inline-media-field">
                    <label>Постер</label>
                    <input name="poster_file" type="file" accept=".jpg,.jpeg,.png,.webp">
                </div>

                <div class="inline-media-field full">
                    <label>Описание</label>
                    <textarea name="alt_text" placeholder="Описание файла для админки и будущего SEO"></textarea>
                </div>

                <div class="inline-media-field full">
                    <button type="submit">Загрузить медиа в проект</button>
                </div>
            </form>

            <div class="inline-media-grid"></div>
        `;

        const grid = panel.querySelector('.inline-media-grid');

        if (data.media_files && data.media_files.length) {
            data.media_files.forEach(function (file) {
                grid.appendChild(createMediaCard(file));
            });
        } else {
            grid.innerHTML = '<div class="inline-media-status">Медиа в этом проекте пока нет.</div>';
        }

        const main = document.querySelector('main') || document.body;
        main.appendChild(panel);
    }

    fetch(`/api/admin/projects/${projectId}/media`, { credentials: 'same-origin' })
        .then(function (response) {
            if (!response.ok) throw new Error('media load error');
            return response.json();
        })
        .then(render)
        .catch(function () {});
})();
