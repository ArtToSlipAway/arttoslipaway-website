/* ATS_CALENDAR_TWO_STATUSES_V2 */
'use strict';

// CITY_DATES_CALENDAR_V6
document.addEventListener('DOMContentLoaded', function () {
    const CITY_NAMES = {
        spb: 'Санкт-Петербург',
        smolensk: 'Смоленск',
        moscow: 'Москва',
        other: 'Другой город'
    };

    const queryParams =
        new URLSearchParams(window.location.search);

    const requestedCity =
        (queryParams.get('city') || '').trim();

    const requestedSlotId =
        (queryParams.get('preferred_slot_id') || '').trim();

    const requestedDateLabel =
        (queryParams.get('preferred_date') || '').trim();

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    let slotsPromise = null;

    function loadSlots() {
        if (!slotsPromise) {
            if (
                typeof window.atsLoadCitySlots === 'function'
            ) {
                slotsPromise =
                    window.atsLoadCitySlots();
            } else {
                slotsPromise = fetch(
                    '/api/city-slots',
                    {
                        method: 'GET',
                        credentials: 'same-origin',
                        cache: 'no-store',
                        headers: {
                            Accept: 'application/json'
                        }
                    }
                ).then(function (response) {
                    if (!response.ok) {
                        throw new Error(
                            'API вернул код '
                            + response.status
                        );
                    }

                    return response.json();
                });
            }
        }

        return slotsPromise;
    }

    function normalizeText(value) {
        return String(value || '')
            .trim()
            .toLocaleLowerCase('ru-RU')
            .replace(/\s+/g, ' ');
    }

    function parseDateKey(value) {
        const match = String(value || '').match(
            /^(\d{4})-(\d{2})-(\d{2})$/
        );

        if (!match) {
            return null;
        }

        return new Date(
            Number(match[1]),
            Number(match[2]) - 1,
            Number(match[3])
        );
    }

    function dateKey(date) {
        const year = date.getFullYear();
        const month = String(
            date.getMonth() + 1
        ).padStart(2, '0');

        const day = String(
            date.getDate()
        ).padStart(2, '0');

        return year + '-' + month + '-' + day;
    }

    function monthStart(date) {
        return new Date(
            date.getFullYear(),
            date.getMonth(),
            1
        );
    }

    function addMonths(date, amount) {
        return new Date(
            date.getFullYear(),
            date.getMonth() + amount,
            1
        );
    }

    function monthLabel(date) {
        const text = new Intl.DateTimeFormat(
            'ru-RU',
            {
                month: 'long',
                year: 'numeric'
            }
        ).format(date);

        return text.charAt(0).toUpperCase() + text.slice(1);
    }

    function formattedDate(date) {
        return new Intl.DateTimeFormat(
            'ru-RU',
            {
                day: 'numeric',
                month: 'long'
            }
        ).format(date);
    }

    function slotStatus(slot) {
        return slot.status === 'booked'
            ? 'booked'
            : 'available';
    }

    // ATS_CALENDAR_PARTIAL_AVAILABILITY_V1
    function slotAvailabilityKind(slot) {
        if (slotStatus(slot) === 'booked') {
            return 'booked';
        }

        const windows =
            Array.isArray(slot.available_windows)
                ? slot.available_windows
                : [];

        if (windows.length) {
            if (
                windows.length === 1 &&
                windows[0] &&
                windows[0].start === '10:00' &&
                windows[0].end === '23:00'
            ) {
                return 'full';
            }

            return 'partial';
        }

        const time =
            normalizeText(slot.slot_time);

        if (
            !time ||
            time === 'весь день' ||
            time === '10:00–23:00' ||
            time === '10:00-23:00'
        ) {
            return 'full';
        }

        return 'partial';
    }

    // ATS_CALENDAR_TIME_READABILITY_V2
    function calendarTimeLabel(slot) {
        const windows =
            Array.isArray(slot.available_windows)
                ? slot.available_windows
                : [];

        if (windows.length) {
            return windows
                .filter(function (windowItem) {
                    return (
                        windowItem &&
                        windowItem.start &&
                        windowItem.end
                    );
                })
                .map(function (windowItem) {
                    return (
                        windowItem.start +
                        '–' +
                        windowItem.end
                    );
                })
                .join(' / ');
        }

        const raw =
            String(slot.slot_time || '').trim();

        const normalized =
            normalizeText(raw);

        if (
            !raw ||
            normalized === 'весь день'
        ) {
            return '10:00–23:00';
        }

        const afterMatch =
            raw.match(
                /^после\s+(\d{1,2})(?::(\d{2}))?$/i
            );

        if (afterMatch) {
            const hour =
                String(afterMatch[1]).padStart(
                    2,
                    '0'
                );

            const minute =
                afterMatch[2] || '00';

            return (
                hour +
                ':' +
                minute +
                '–23:00'
            );
        }

        const beforeMatch =
            raw.match(
                /^до\s+(\d{1,2})(?::(\d{2}))?$/i
            );

        if (beforeMatch) {
            const hour =
                String(beforeMatch[1]).padStart(
                    2,
                    '0'
                );

            const minute =
                beforeMatch[2] || '00';

            return (
                '10:00–' +
                hour +
                ':' +
                minute
            );
        }

        return raw;
    }


    function slotDetails(slot, includeDate) {
        const parts = [];

        if (includeDate) {
            if (slot.date_label) {
                parts.push(slot.date_label);
            } else if (slot.slot_date) {
                const parsed = parseDateKey(slot.slot_date);

                if (parsed) {
                    parts.push(formattedDate(parsed));
                }
            }
        }

        if (slot.slot_time) {
            parts.push(slot.slot_time);
        }


        return parts.join(' · ') ||
            (includeDate
                ? 'По договорённости'
                : 'Свободное время');
    }

    function storedValue(city, slot) {
        return (
            (CITY_NAMES[city] || city) +
            ' — ' +
            slotDetails(slot, true)
        );
    }

    function initCalendar(config) {
        const form =
            document.getElementById(config.formId);

        const citySelect =
            document.getElementById(config.cityId);

        const preferredInput =
            document.getElementById(config.inputId);

        if (!form || !citySelect || !preferredInput) {
            return;
        }

        const field =
            preferredInput.closest('.city-dates-field') ||
            preferredInput.closest('.field') ||
            preferredInput.parentElement;

        if (!field) {
            return;
        }

        field
            .querySelectorAll(
                '.city-dates-status, .city-dates-list'
            )
            .forEach(function (element) {
                element.hidden = true;
                element.style.display = 'none';
            });

        let mount =
            field.querySelector('.ats-city-calendar');

        if (!mount) {
            mount = document.createElement('div');
            mount.className = 'ats-city-calendar';
            preferredInput.insertAdjacentElement(
                'afterend',
                mount
            );
        }

        // ATS_CALENDAR_AGREEMENT_INPUT_V1
        const state = {
            data: null,
            city: '',
            viewMonth: monthStart(today),
            selectedDate: '',
            selectedSlotId: '',
            agreementText: '',
            prefillApplied: false
        };

        function setFieldVisible(visible) {
            field.hidden = !visible;

            field.style.setProperty(
                'display',
                visible ? 'block' : 'none',
                'important'
            );
        }

        function clearSelection() {
            state.selectedDate = '';
            state.selectedSlotId = '';
            state.agreementText = '';
            preferredInput.value = '';
        }

        function citySlots(city) {
            if (
                !state.data ||
                !Array.isArray(state.data[city])
            ) {
                return [];
            }

            return state.data[city];
        }

        function selectSlot(city, slot) {
            if (slotStatus(slot) !== 'available') {
                return;
            }

            const slotId = String(slot.id || '');
            const isUndated = !slot.slot_date;
            const sameSlot =
                state.selectedSlotId === slotId;

            if (!sameSlot || !isUndated) {
                state.agreementText = '';
            }

            state.selectedSlotId = slotId;
            state.selectedDate = String(
                slot.slot_date || ''
            );

            if (isUndated) {
                const agreement =
                    state.agreementText.trim();

                preferredInput.value = agreement
                    ? storedValue(city, slot) +
                      ' — удобно: ' +
                      agreement
                    : '';
            } else {
                state.agreementText = '';

                preferredInput.value =
                    storedValue(city, slot);
            }
        }

        function chooseInitialMonth(slots) {
            const dated = slots
                .filter(function (slot) {
                    return Boolean(slot.slot_date);
                })
                .map(function (slot) {
                    return parseDateKey(slot.slot_date);
                })
                .filter(Boolean)
                .sort(function (a, b) {
                    return a - b;
                });

            state.viewMonth = dated.length
                ? monthStart(dated[0])
                : monthStart(today);
        }

        function applyPrefill(city, slots) {
            if (
                state.prefillApplied ||
                (requestedCity && requestedCity !== city)
            ) {
                return false;
            }

            let found = null;

            if (requestedSlotId) {
                found = slots.find(function (slot) {
                    return (
                        String(slot.id || '') ===
                        requestedSlotId
                    );
                });
            }

            if (!found && requestedDateLabel) {
                const requested =
                    normalizeText(requestedDateLabel);

                found = slots.find(function (slot) {
                    return (
                        normalizeText(slot.date_label) ===
                        requested
                    );
                });
            }

            state.prefillApplied = true;

            if (
                !found ||
                slotStatus(found) !== 'available'
            ) {
                return false;
            }

            selectSlot(city, found);

            if (found.slot_date) {
                const parsed =
                    parseDateKey(found.slot_date);

                if (parsed) {
                    state.viewMonth =
                        monthStart(parsed);
                }
            }

            return true;
        }

        function showMessage(text, error) {
            mount.innerHTML = '';

            const message =
                document.createElement('div');

            message.className =
                'ats-calendar-message' +
                (error ? ' is-error' : '');

            message.textContent = text;

            mount.appendChild(message);
        }

        function renderCalendar(city, slots) {
            const datedByDay = new Map();
            const undated = [];

            slots.forEach(function (slot) {
                if (!slot.slot_date) {
                    undated.push(slot);
                    return;
                }

                if (!datedByDay.has(slot.slot_date)) {
                    datedByDay.set(
                        slot.slot_date,
                        []
                    );
                }

                datedByDay
                    .get(slot.slot_date)
                    .push(slot);
            });

            mount.innerHTML = `
                <div class="ats-calendar-shell">
                    <div class="ats-calendar-toolbar">
                        <button
                            type="button"
                            class="ats-calendar-nav"
                            data-calendar-prev
                            aria-label="Предыдущий месяц"
                        >‹</button>

                        <div
                            class="ats-calendar-month"
                            data-calendar-month
                        ></div>

                        <button
                            type="button"
                            class="ats-calendar-nav"
                            data-calendar-next
                            aria-label="Следующий месяц"
                        >›</button>
                    </div>

                    <div class="ats-calendar-weekdays">
                        <span>Пн</span>
                        <span>Вт</span>
                        <span>Ср</span>
                        <span>Чт</span>
                        <span>Пт</span>
                        <span>Сб</span>
                        <span>Вс</span>
                    </div>

                    <div
                        class="ats-calendar-grid"
                        data-calendar-grid
                    ></div>

                    <div
                        class="ats-calendar-slots"
                        data-calendar-slots
                    ></div>

                    <div
                        class="ats-calendar-undated"
                        data-calendar-undated
                    ></div>

                    <div class="ats-calendar-legend">
                        <span>
                            <i class="is-free"></i>
                            Свободен весь день
                        </span>
                        <span>
                            <i class="is-partial"></i>
                            Есть свободное время
                        </span>
                        <span>
                            <i class="is-busy"></i>
                            Занято
                        </span>
                    </div>
                </div>
            `;

            const monthTitle =
                mount.querySelector(
                    '[data-calendar-month]'
                );

            const grid =
                mount.querySelector(
                    '[data-calendar-grid]'
                );

            const slotsBox =
                mount.querySelector(
                    '[data-calendar-slots]'
                );

            const undatedBox =
                mount.querySelector(
                    '[data-calendar-undated]'
                );

            const prev =
                mount.querySelector(
                    '[data-calendar-prev]'
                );

            const next =
                mount.querySelector(
                    '[data-calendar-next]'
                );

            monthTitle.textContent =
                monthLabel(state.viewMonth);

            const firstDay = new Date(
                state.viewMonth.getFullYear(),
                state.viewMonth.getMonth(),
                1
            );

            const daysInMonth = new Date(
                state.viewMonth.getFullYear(),
                state.viewMonth.getMonth() + 1,
                0
            ).getDate();

            const mondayOffset =
                (firstDay.getDay() + 6) % 7;

            for (
                let emptyIndex = 0;
                emptyIndex < mondayOffset;
                emptyIndex += 1
            ) {
                const empty =
                    document.createElement('span');

                empty.className =
                    'ats-calendar-day is-empty';

                grid.appendChild(empty);
            }

            for (
                let dayNumber = 1;
                dayNumber <= daysInMonth;
                dayNumber += 1
            ) {
                const date = new Date(
                    state.viewMonth.getFullYear(),
                    state.viewMonth.getMonth(),
                    dayNumber
                );

                const key = dateKey(date);
                const daySlots =
                    datedByDay.get(key) || [];

                const available = daySlots.filter(
                    function (slot) {
                        return (
                            slotStatus(slot) ===
                            'available'
                        );
                    }
                );

                const booked = daySlots.filter(
                    function (slot) {
                        return (
                            slotStatus(slot) ===
                            'booked'
                        );
                    }
                );

                const hasFullAvailability =
                    available.some(
                        function (slot) {
                            return (
                                slotAvailabilityKind(slot) ===
                                'full'
                            );
                        }
                    );

                const isPartialAvailability =
                    available.length > 0 &&
                    !hasFullAvailability;

                // ATS_CALENDAR_DARK_OZON_BRONZE_V4
                //
                // Если единственное доступное окно —
                // 21:00–23:00, визуально делаем
                // такую дату значительно темнее.
                //
                // Это типичный день со сменой OZON.
                const isLateOnlyAvailability =
                    isPartialAvailability &&
                    available.length > 0 &&
                    available.every(
                        function (slot) {

                            const windows =
                                Array.isArray(
                                    slot.available_windows
                                )
                                    ? slot.available_windows
                                    : [];

                            if (
                                windows.length === 1 &&
                                windows[0] &&
                                windows[0].start ===
                                    '21:00' &&
                                windows[0].end ===
                                    '23:00'
                            ) {
                                return true;
                            }

                            const time =
                                normalizeText(
                                    slot.slot_time
                                );

                            return (
                                time === 'после 21:00' ||
                                time === 'после 21'
                            );
                        }
                    );

                const isPast = date < today;

                const button =
                    document.createElement('button');

                button.type = 'button';
                button.className =
                    'ats-calendar-day';

                button.textContent =
                    String(dayNumber);

                if (isPast) {
                    button.classList.add('is-booked');
                    button.disabled = true;
                    button.title = 'Занято';
                } else if (available.length) {
                    button.classList.add(
                        isPartialAvailability
                            ? 'is-partial'
                            : 'is-available'
                    );

                    if (isLateOnlyAvailability) {
                        button.classList.add(
                            'is-late-only'
                        );
                    }

                    if (isPartialAvailability) {
                        button.title =
                            'Частично свободно: ' +
                            available
                                .map(function (slot) {
                                    return slotDetails(
                                        slot,
                                        false
                                    );
                                })
                                .join(' / ');
                    } else {
                        button.title =
                            available.length === 1
                                ? 'Свободная дата'
                                : 'Есть несколько вариантов';
                    }
                } else if (booked.length) {
                    button.classList.add(
                        'is-booked'
                    );

                    button.disabled = true;
                    button.title = 'Занято';
                } else {
                    button.classList.add(
                        'is-booked'
                    );

                    button.disabled = true;
                    button.title = 'Занято';
                }

                if (
                    !isPast &&
                    available.length
                ) {
                    // ATS_CALENDAR_FULL_DAY_TEXT_V1
                    const timeLabel =
                        document.createElement(
                            'span'
                        );

                    timeLabel.className =
                        'ats-calendar-day-time';

                    if (hasFullAvailability) {

                        timeLabel.classList.add(
                            'is-full-day'
                        );

                        timeLabel.textContent =
                            'ВЕСЬ ДЕНЬ';

                    } else {

                        const labels = [];

                        available.forEach(
                            function (slot) {
                                const label =
                                    calendarTimeLabel(
                                        slot
                                    );

                                if (
                                    label &&
                                    !labels.includes(label)
                                ) {
                                    labels.push(label);
                                }
                            }
                        );

                        timeLabel.textContent =
                            'ВРЕМЯ\n' +
                            labels.join(' / ');
                    }

                    button.appendChild(
                        timeLabel
                    );
                }

                if (state.selectedDate === key) {
                    button.classList.add(
                        'is-selected'
                    );
                }

                if (
                    !isPast &&
                    available.length
                ) {
                    button.addEventListener(
                        'click',
                        function () {
                            state.selectedDate = key;
                            state.selectedSlotId = '';
                            preferredInput.value = '';

                            if (available.length === 1) {
                                selectSlot(
                                    city,
                                    available[0]
                                );
                            }

                            renderCalendar(
                                city,
                                slots
                            );
                        }
                    );
                }

                grid.appendChild(button);
            }

            const maxMonth =
                addMonths(
                    monthStart(today),
                    1
                );

            prev.disabled =
                state.viewMonth <= monthStart(today);

            next.disabled =
                state.viewMonth >= maxMonth;

            prev.addEventListener(
                'click',
                function () {
                    state.viewMonth =
                        addMonths(
                            state.viewMonth,
                            -1
                        );

                    renderCalendar(city, slots);
                }
            );

            next.addEventListener(
                'click',
                function () {
                    if (
                        state.viewMonth >=
                        maxMonth
                    ) {
                        return;
                    }

                    state.viewMonth =
                        addMonths(
                            state.viewMonth,
                            1
                        );

                    renderCalendar(city, slots);
                }
            );

            if (state.selectedDate) {
                const selectedDate =
                    parseDateKey(
                        state.selectedDate
                    );

                const selectedSlots =
                    datedByDay.get(
                        state.selectedDate
                    ) || [];

                const title =
                    document.createElement('div');

                title.className =
                    'ats-calendar-slots-title';

                title.textContent =
                    selectedDate
                        ? 'Варианты на ' +
                          formattedDate(selectedDate)
                        : 'Выбери время';

                slotsBox.appendChild(title);

                selectedSlots.forEach(
                    function (slot) {
                        const button =
                            document.createElement(
                                'button'
                            );

                        button.type = 'button';
                        button.className =
                            'ats-calendar-slot';

                        button.textContent =
                            slotDetails(slot, false);

                        if (
                            slotStatus(slot) ===
                            'booked'
                        ) {
                            button.disabled = true;
                            button.classList.add(
                                'is-booked'
                            );

                            button.textContent +=
                                ' · занято';
                        } else {
                            button.addEventListener(
                                'click',
                                function () {
                                    selectSlot(
                                        city,
                                        slot
                                    );

                                    renderCalendar(
                                        city,
                                        slots
                                    );
                                }
                            );
                        }

                        if (
                            state.selectedSlotId ===
                            String(slot.id || '')
                        ) {
                            button.classList.add(
                                'is-selected'
                            );
                        }

                        slotsBox.appendChild(button);
                    }
                );
            } else {
                slotsBox.textContent =
                    'Выбери золотую дату в календаре.';
            }

            if (undated.length) {
                const title =
                    document.createElement('div');

                title.className =
                    'ats-calendar-slots-title';

                title.textContent =
                    'Другие варианты';

                undatedBox.appendChild(title);

                undated.forEach(function (slot) {
                    const button =
                        document.createElement(
                            'button'
                        );

                    button.type = 'button';
                    button.className =
                        'ats-calendar-slot';

                    button.textContent =
                        slotDetails(slot, true);

                    if (
                        slotStatus(slot) ===
                        'booked'
                    ) {
                        button.disabled = true;
                        button.classList.add(
                            'is-booked'
                        );
                    } else {
                        button.addEventListener(
                            'click',
                            function () {
                                selectSlot(
                                    city,
                                    slot
                                );

                                renderCalendar(
                                    city,
                                    slots
                                );
                            }
                        );
                    }

                    if (
                        state.selectedSlotId ===
                        String(slot.id || '')
                    ) {
                        button.classList.add(
                            'is-selected'
                        );
                    }

                    undatedBox.appendChild(button);
                });

                const selectedUndated =
                    undated.find(function (slot) {
                        return (
                            String(slot.id || '') ===
                                state.selectedSlotId &&
                            slotStatus(slot) ===
                                'available'
                        );
                    });

                if (selectedUndated) {
                    const agreementBox =
                        document.createElement('div');

                    agreementBox.className =
                        'ats-calendar-agreement';

                    const agreementLabel =
                        document.createElement('label');

                    const agreementInput =
                        document.createElement('textarea');

                    agreementInput.id =
                        config.inputId +
                        '_agreement';

                    agreementInput.className =
                        'ats-calendar-agreement-input';

                    agreementInput.rows = 3;
                    agreementInput.maxLength = 300;

                    agreementInput.placeholder =
                        'Например: после 10 августа, желательно в выходной после 14:00';

                    agreementInput.value =
                        state.agreementText;

                    agreementLabel.className =
                        'ats-calendar-agreement-label';

                    agreementLabel.htmlFor =
                        agreementInput.id;

                    agreementLabel.textContent =
                        'Напиши, когда тебе удобно';

                    const agreementHint =
                        document.createElement('div');

                    agreementHint.className =
                        'ats-calendar-agreement-hint';

                    agreementHint.textContent =
                        'Можно указать несколько подходящих дней, время или период.';

                    agreementInput.addEventListener(
                        'input',
                        function () {
                            state.agreementText =
                                agreementInput.value;

                            const agreement =
                                state.agreementText.trim();

                            preferredInput.value =
                                agreement
                                    ? storedValue(
                                          city,
                                          selectedUndated
                                      ) +
                                      ' — удобно: ' +
                                      agreement
                                    : '';

                            const oldError =
                                mount.querySelector(
                                    '.ats-calendar-validation'
                                );

                            if (oldError && agreement) {
                                oldError.remove();
                            }
                        }
                    );

                    agreementBox.appendChild(
                        agreementLabel
                    );

                    agreementBox.appendChild(
                        agreementInput
                    );

                    agreementBox.appendChild(
                        agreementHint
                    );

                    undatedBox.appendChild(
                        agreementBox
                    );
                }

            }
        }

        async function refresh(resetCity) {
            const city = citySelect.value;

            if (!city) {
                setFieldVisible(false);
                clearSelection();
                mount.innerHTML = '';
                return;
            }

            setFieldVisible(true);

            if (resetCity || state.city !== city) {
                state.city = city;
                clearSelection();
            }

            if (city === 'other') {
                preferredInput.value =
                    'Другой город — дату и возможность выезда обсудим лично';

                showMessage(
                    'Дату и возможность выезда обсудим лично.',
                    false
                );

                field.dataset.hasSlots = 'false';
                return;
            }

            showMessage(
                'Загружаю календарь…',
                false
            );

            try {
                state.data = await loadSlots();

                const slots = citySlots(city);
                const available = slots.filter(
                    function (slot) {
                        return (
                            slotStatus(slot) ===
                            'available'
                        );
                    }
                );

                field.dataset.hasSlots =
                    available.length
                        ? 'true'
                        : 'false';

                if (!slots.length) {
                    showMessage(
                        'Сейчас для этого города нет опубликованных дат. Отправь заявку — я предложу варианты лично.',
                        false
                    );

                    return;
                }

                const prefilled =
                    applyPrefill(city, slots);

                if (!prefilled && resetCity) {
                    chooseInitialMonth(slots);
                }

                const datedAvailable =
                    available.filter(
                        function (slot) {
                            return Boolean(
                                slot.slot_date
                            );
                        }
                    );

                const undatedAvailable =
                    available.filter(
                        function (slot) {
                            return !slot.slot_date;
                        }
                    );

                if (
                    !prefilled &&
                    datedAvailable.length === 0 &&
                    undatedAvailable.length === 1
                ) {
                    selectSlot(
                        city,
                        undatedAvailable[0]
                    );
                }

                renderCalendar(city, slots);
            } catch (error) {
                console.error(
                    'Не удалось загрузить календарь:',
                    error
                );

                field.dataset.hasSlots = 'false';

                showMessage(
                    'Не удалось загрузить календарь. Заявку можно отправить без выбора даты.',
                    true
                );
            }
        }

        citySelect.addEventListener(
            'change',
            function () {
                refresh(true);
            }
        );

        form.addEventListener(
            'submit',
            function (event) {
                const city = citySelect.value;
                const slots = citySlots(city);

                const hasAvailable =
                    slots.some(function (slot) {
                        return (
                            slotStatus(slot) ===
                            'available'
                        );
                    });

                const selectedSlot =
                    slots.find(function (slot) {
                        return (
                            String(slot.id || '') ===
                            state.selectedSlotId
                        );
                    });

                const needsAgreementText =
                    Boolean(
                        selectedSlot &&
                        !selectedSlot.slot_date &&
                        slotStatus(selectedSlot) ===
                            'available'
                    );

                if (
                    city &&
                    city !== 'other' &&
                    hasAvailable &&
                    !preferredInput.value.trim()
                ) {
                    event.preventDefault();

                    const oldError =
                        mount.querySelector(
                            '.ats-calendar-validation'
                        );

                    if (oldError) {
                        oldError.remove();
                    }

                    const error =
                        document.createElement('div');

                    error.className =
                        'ats-calendar-validation';

                    error.textContent =
                        needsAgreementText
                            ? 'Напиши, когда тебе удобно приехать.'
                            : 'Выбери свободную дату и время.';

                    mount.prepend(error);

                    field.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });

                    if (needsAgreementText) {
                        const agreementInput =
                            mount.querySelector(
                                '.ats-calendar-agreement-input'
                            );

                        if (agreementInput) {
                            agreementInput.focus();
                        }
                    }
                }
            }
        );

        if (requestedCity) {
            const option =
                citySelect.querySelector(
                    'option[value="' +
                    requestedCity +
                    '"]'
                );

            if (option) {
                citySelect.value =
                    requestedCity;
            }
        }

        refresh(true);
    }

    initCalendar({
        formId: 'quickLeadForm',
        cityId: 'quick_city',
        inputId: 'quick_preferred_dates'
    });

    initCalendar({
        formId: 'leadForm',
        cityId: 'city',
        inputId: 'preferred_dates'
    });
});
