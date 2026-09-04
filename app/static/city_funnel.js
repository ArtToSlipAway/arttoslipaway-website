(function () {
    const CITY_LABELS = {
        spb: 'Санкт-Петербург',
        smolensk: 'Смоленск',
        moscow: 'Москва'
    };

    function cityFromText(text) {
        const clean = (text || '').trim().toLowerCase();

        if (clean.includes('санкт')) return 'spb';
        if (clean.includes('петербург')) return 'spb';
        if (clean.includes('смоленск')) return 'smolensk';
        if (clean.includes('москва')) return 'moscow';

        return '';
    }

    // CITY_FOOTER_DATE_PREFILL_V3
    function requestUrl(city, dateLabel, slotId) {
        const params = new URLSearchParams();

        params.set('source', 'city');
        params.set('service', 'tattoo');
        params.set('city', city);

        if (dateLabel) {
            params.set('preferred_date', dateLabel);
        }

        if (slotId) {
            params.set(
                'preferred_slot_id',
                String(slotId)
            );
        }

        return '/request?' + params.toString();
    }

    function installStyles() {
        if (document.getElementById('cityFunnelStyles')) return;

        const style = document.createElement('style');
        style.id = 'cityFunnelStyles';

        style.textContent = `
            .work-cities .city-item {
                pointer-events: auto !important;
                cursor: pointer !important;
            }

            .city-funnel-link {
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: flex-end !important;
                width: 100% !important;
                color: inherit !important;
                text-decoration: none !important;
                pointer-events: auto !important;
            }

            .city-funnel-link * {
                pointer-events: auto !important;
            }

            .city-free-dates {
                display: flex !important;
                flex-wrap: wrap !important;
                justify-content: center !important;
                gap: 6px !important;
                margin-top: 9px !important;
                min-height: 26px !important;
            }

            .city-date-chip,
            .city-date-empty {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                min-height: 24px !important;
                padding: 5px 8px !important;
                border-radius: 999px !important;

                font-family: Arial, sans-serif !important;
                font-size: 11px !important;
                line-height: 1 !important;
                letter-spacing: 0.045em !important;

                border: 1px solid rgba(201, 163, 58, 0.38) !important;
                background: rgba(0, 0, 0, 0.38) !important;
                color: rgba(232, 221, 198, 0.82) !important;
                text-decoration: none !important;
            }

            .city-date-chip:hover {
                border-color: #f2d984 !important;
                color: #111 !important;
                background: #f2d984 !important;
                box-shadow:
                    0 0 10px rgba(242, 217, 132, 0.36),
                    0 0 22px rgba(201, 163, 58, 0.18) !important;
            }

            .city-date-empty {
                opacity: 0.56 !important;
            }

            @media (max-width: 900px) {
                .city-free-dates {
                    margin-top: 7px !important;
                }

                .city-date-chip,
                .city-date-empty {
                    font-size: 10px !important;
                    min-height: 22px !important;
                }
            }
        `;

        document.head.appendChild(style);
    }

    function makeCityClickable(cityItem, city) {
        if (!cityItem || !city) return;

        if (cityItem.querySelector('.city-funnel-link')) return;

        const children = Array.from(cityItem.childNodes);
        const link = document.createElement('a');

        link.className = 'city-funnel-link';
        link.href = requestUrl(city, '', '');
        link.setAttribute('data-city', city);
        link.setAttribute('aria-label', 'Оставить заявку: ' + CITY_LABELS[city]);

        children.forEach(function (child) {
            link.appendChild(child);
        });

        cityItem.appendChild(link);
    }

    function installCityDates(slotsByCity) {
        const cityItems = Array.from(document.querySelectorAll('.work-cities .city-item'));

        cityItems.forEach(function (item) {
            const nameEl = item.querySelector('.city-name');
            const city = cityFromText(nameEl ? nameEl.textContent : item.textContent);

            if (!city) return;

            makeCityClickable(item, city);

            const link = item.querySelector('.city-funnel-link');
            if (!link) return;

            let dates = link.querySelector('.city-free-dates');

            if (!dates) {
                dates = document.createElement('div');
                dates.className = 'city-free-dates';
                link.appendChild(dates);
            }

            dates.innerHTML = '';

            const rawSlots =
                (slotsByCity && Array.isArray(slotsByCity[city]))
                    ? slotsByCity[city]
                    : [];

            // ATS_HOME_FULL_DAY_DATES_ONLY_V1
            //
            // На главной показываем только даты,
            // свободные на всё рабочее окно
            // студии 10:00–23:00.
            //
            // Частично свободные даты остаются
            // доступны в полном календаре /request.
            const slots = rawSlots.filter(function (slot) {

                if (
                    (slot.status || 'available') !==
                    'available'
                ) {
                    return false;
                }

                const windows =
                    Array.isArray(slot.available_windows)
                        ? slot.available_windows
                        : [];

                if (windows.length) {
                    return (
                        windows.length === 1 &&
                        windows[0] &&
                        windows[0].start === '10:00' &&
                        windows[0].end === '23:00'
                    );
                }

                /*
                 * Совместимость со старыми /
                 * ручными слотами без
                 * available_windows.
                 */
                const slotTime =
                    String(slot.slot_time || '')
                        .trim()
                        .toLocaleLowerCase('ru-RU');

                return (
                    slotTime === 'весь день' ||
                    slotTime === '10:00–23:00' ||
                    slotTime === '10:00-23:00'
                );
            });

            // ATS_HOME_FULL_DAY_RENDER_GUARD_V2
            //
            // Финальный фильтр непосредственно
            // перед рендером трёх кнопок.
            const displaySlots = slots.filter(
                function (slot) {

                    if (
                        (slot.status || 'available') !==
                        'available'
                    ) {
                        return false;
                    }

                    const windows =
                        Array.isArray(
                            slot.available_windows
                        )
                            ? slot.available_windows
                            : [];

                    if (windows.length) {
                        return (
                            windows.length === 1 &&
                            windows[0] &&
                            windows[0].start ===
                                '10:00' &&
                            windows[0].end ===
                                '23:00'
                        );
                    }

                    const time =
                        String(
                            slot.slot_time || ''
                        )
                            .trim()
                            .toLocaleLowerCase(
                                'ru-RU'
                            );

                    return (
                        time === 'весь день' ||
                        time === '10:00–23:00' ||
                        time === '10:00-23:00'
                    );
                }
            );

            if (!displaySlots.length) {
                const empty = document.createElement('span');
                empty.className = 'city-date-empty';
                empty.textContent = 'Даты уточняются';
                dates.appendChild(empty);
                return;
            }

            displaySlots.slice(0, 3).forEach(function (slot) {
                const chip = document.createElement('a');
                chip.className = 'city-date-chip';
                chip.href = requestUrl(
                    city,
                    slot.date_label,
                    slot.id
                );
                chip.textContent = slot.date_label;
                chip.addEventListener('click', function (event) {
                    event.stopPropagation();
                });

                dates.appendChild(chip);
            });
        });
    }

    // ATS_SHARED_CITY_SLOTS_PROMISE_V1
    //
    // Один HTTP-запрос /api/city-slots на загрузку страницы.
    // Главная, footer funnel и форма используют один Promise.
    function loadCitySlotsShared() {
        if (!window.__atsCitySlotsPromise) {
            window.__atsCitySlotsPromise = fetch(
                '/api/city-slots',
                {
                    method: 'GET',
                    credentials: 'same-origin',
                    cache: 'no-store',
                    headers: {
                        Accept: 'application/json'
                    }
                }
            )
            .then(function (response) {
                if (!response.ok) {
                    throw new Error(
                        'city slots api error: '
                        + response.status
                    );
                }

                return response.json();
            })
            .catch(function (error) {
                // Разрешаем повторную попытку после ошибки.
                window.__atsCitySlotsPromise = null;
                throw error;
            });
        }

        return window.__atsCitySlotsPromise;
    }

    window.atsLoadCitySlots = loadCitySlotsShared;


    function setupFooterCityFunnel() {
        if (!document.querySelector('.work-cities')) return;

        installStyles();

        loadCitySlotsShared()
            .then(function (data) {
                installCityDates(data);
            })
            .catch(function () {
                installCityDates({
                    spb: [],
                    smolensk: [],
                    moscow: []
                });
            });
    }

    function setupRequestPrefill() {
        if (window.location.pathname !== '/request') return;

        const params = new URLSearchParams(window.location.search);

        const city = params.get('city');
        const service = params.get('service');
        const citySelect = document.getElementById('city');
        const serviceSelect = document.getElementById('service_type');

        if (service && serviceSelect) {
            const option = serviceSelect.querySelector('option[value="' + service + '"]');
            if (option) {
                serviceSelect.value = service;
                serviceSelect.dispatchEvent(new Event('change'));
            }
        }

        if (city && citySelect) {
            const option = citySelect.querySelector('option[value="' + city + '"]');
            if (option) {
                citySelect.value = city;
            }
        }

    }

    function boot() {
        setupFooterCityFunnel();
        setupRequestPrefill();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
