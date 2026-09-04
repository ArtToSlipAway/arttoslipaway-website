(function () {
    function normalizePath(path) {
        if (!path) return '/';
        if (path.length > 1) {
            return path.replace(/\/+$/, '');
        }
        return path;
    }

    const currentPath = normalizePath(window.location.pathname);

    document.querySelectorAll('.admin-nav a').forEach(function (link) {
        const href = normalizePath(link.getAttribute('href') || '');

        if (!href || href === '/') {
            return;
        }

        if (href === '/admin' && currentPath === '/admin') {
            link.classList.add('is-active');
            return;
        }

        if (href !== '/admin' && currentPath.startsWith(href)) {
            link.classList.add('is-active');
        }
    });

    document.querySelectorAll('button, .button, input[type="submit"]').forEach(function (button) {
        const text = (button.textContent || button.value || '').trim().toLowerCase();

        if (
            text.includes('удалить') ||
            text.includes('delete') ||
            text.includes('trash')
        ) {
            button.classList.add('admin-danger-button');
        }

        if (
            text.includes('сохранить') ||
            text.includes('добавить') ||
            text.includes('загрузить') ||
            text.includes('создать')
        ) {
            button.classList.add('admin-primary-button');
        }
    });

    document.querySelectorAll('form').forEach(function (form) {
        const hasFileInput = form.querySelector('input[type="file"]');

        if (hasFileInput) {
            form.classList.add('admin-upload-form');
        }
    });
})();
