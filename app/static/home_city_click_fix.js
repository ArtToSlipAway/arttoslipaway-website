'use strict';

/* ATS_HOME_CITY_CLICK_HARDFIX_V2 */

(function () {
    const CITY_MAP = [
        {
            text: 'санкт-петербург',
            code: 'spb'
        },
        {
            text: 'смоленск',
            code: 'smolensk'
        },
        {
            text: 'москва',
            code: 'moscow'
        }
    ];

    function getCityCode(item) {
        if (!item) {
            return null;
        }

        const text = String(
            item.textContent || ''
        ).toLowerCase();

        for (const city of CITY_MAP) {
            if (text.includes(city.text)) {
                return city.code;
            }
        }

        return null;
    }

    function cityUrl(code) {
        return (
            '/request' +
            '?source=city' +
            '&service=tattoo' +
            '&city=' +
            encodeURIComponent(code)
        );
    }

    function prepareItems() {
        document
            .querySelectorAll('.work-cities .city-item')
            .forEach(function (item) {
                const code = getCityCode(item);

                if (!code) {
                    return;
                }

                item.dataset.atsCityCode = code;

                item.style.cursor = 'pointer';
                item.style.pointerEvents = 'auto';
                item.style.position = 'relative';
                item.style.zIndex = '20';

                item.setAttribute('role', 'link');
                item.setAttribute('tabindex', '0');
                item.setAttribute(
                    'aria-label',
                    'Открыть запись: ' +
                    String(item.textContent || '').trim()
                );

                item.querySelectorAll('img').forEach(
                    function (img) {
                        img.style.pointerEvents = 'none';
                    }
                );
            });

        const block =
            document.querySelector('.work-cities');

        if (block) {
            block.style.position = 'relative';
            block.style.zIndex = '20';
            block.style.pointerEvents = 'auto';
        }
    }

    function itemFromPoint(x, y) {
        const items =
            document.querySelectorAll(
                '.work-cities .city-item'
            );

        for (const item of items) {
            const rect =
                item.getBoundingClientRect();

            if (
                x >= rect.left &&
                x <= rect.right &&
                y >= rect.top &&
                y <= rect.bottom
            ) {
                return item;
            }
        }

        return null;
    }

    function findItem(event) {
        if (
            event.target &&
            event.target.closest
        ) {
            const direct =
                event.target.closest(
                    '.work-cities .city-item'
                );

            if (direct) {
                return direct;
            }
        }

        return itemFromPoint(
            event.clientX,
            event.clientY
        );
    }

    document.addEventListener(
        'click',
        function (event) {
            const item = findItem(event);

            if (!item) {
                return;
            }

            const code =
                item.dataset.atsCityCode ||
                getCityCode(item);

            if (!code) {
                return;
            }

            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();

            window.location.assign(
                cityUrl(code)
            );
        },
        true
    );

    document.addEventListener(
        'keydown',
        function (event) {
            if (
                event.key !== 'Enter' &&
                event.key !== ' '
            ) {
                return;
            }

            const item =
                event.target &&
                event.target.closest
                    ? event.target.closest(
                        '.work-cities .city-item'
                    )
                    : null;

            if (!item) {
                return;
            }

            const code =
                item.dataset.atsCityCode ||
                getCityCode(item);

            if (!code) {
                return;
            }

            event.preventDefault();

            window.location.assign(
                cityUrl(code)
            );
        },
        true
    );

    if (
        document.readyState === 'loading'
    ) {
        document.addEventListener(
            'DOMContentLoaded',
            prepareItems
        );
    } else {
        prepareItems();
    }
})();
