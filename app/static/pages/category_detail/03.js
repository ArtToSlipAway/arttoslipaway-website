(function () {
            if (window.location.pathname !== '/categories/paintings') return;

            function removeStray3DButton() {
                document.querySelectorAll('a, button, [role="button"]').forEach(function (element) {
                    const label = (element.textContent || '')
                        .replace(/\s+/g, ' ')
                        .trim()
                        .toUpperCase();

                    if (label === 'СМОТРЕТЬ 3D') {
                        element.remove();
                    }
                });
            }

            document.addEventListener('DOMContentLoaded', removeStray3DButton);
            removeStray3DButton();

            new MutationObserver(removeStray3DButton).observe(document.documentElement, {
                childList: true,
                subtree: true
            });
        })();
