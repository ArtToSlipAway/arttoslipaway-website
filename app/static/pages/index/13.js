document.addEventListener('DOMContentLoaded', function () {

    (
        typeof window.atsLoadCitySlots === 'function'
            ? window.atsLoadCitySlots()
            : fetch('/api/city-slots', {
                cache: 'no-store'
            }).then(function(r){
                return r.json();
            })
    )
    .then(function(data){

        const cities = {
            spb: 'Санкт-Петербург',
            smolensk: 'Смоленск',
            moscow: 'Москва'
        };

        Object.keys(cities).forEach(function(city){

            const slots = data[city] || [];

            const dates = slots
                .filter(function(slot){
                    return (
                        slot.slot_date &&
                        (
                            slot.status === 'available' ||
                            slot.slot_status === 'available'
                        )
                    );
                })
                // ATS_HOME_INLINE_FULL_DAY_ONLY_V1
                .filter(function(slot){

                    /*
                     * Этот старый inline-рендерер
                     * тоже должен показывать на
                     * главной только полностью
                     * свободные дни 10:00–23:00.
                     */

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

                    const slotTime =
                        String(
                            slot.slot_time || ''
                        )
                            .trim()
                            .toLocaleLowerCase(
                                'ru-RU'
                            );

                    return (
                        slotTime === 'весь день' ||
                        slotTime === '10:00–23:00' ||
                        slotTime === '10:00-23:00'
                    );

                })
                .sort(function(a,b){
                    return new Date(a.slot_date) - new Date(b.slot_date);
                })
                .slice(0,3)
                .map(function(slot){

                    return new Date(slot.slot_date)
                        .toLocaleDateString(
                            'ru-RU',
                            {
                                day:'numeric',
                                month:'long'
                            }
                        );

                });


            const cityBlocks =
                document.querySelectorAll('.city-name');


            cityBlocks.forEach(function(block){

                if(block.textContent.trim() === cities[city]){

                    let dateBlock =
                        block.parentElement.querySelector('.city-free-dates');

                    if(!dateBlock){

                        dateBlock =
                            document.createElement('div');

                        dateBlock.className =
                            'city-free-dates';

                        block.after(dateBlock);
                    }


                    if (
                        city === 'spb' &&
                        dates.length
                    ) {
                        dateBlock.textContent = '';

                        const label =
                            document.createElement('span');

                        label.className =
                            'ats-dates-label';

                        label.textContent =
                            'Свободно:';

                        dateBlock.appendChild(label);

                        dates.forEach(function(date) {
                            const button =
                                document.createElement('span');

                            button.className =
                                'ats-date-button';

                            button.textContent = date;

                            dateBlock.appendChild(button);
                        });
                    } else {
                        dateBlock.textContent =
                            'Свободные даты уточняются';
                    }

                }

            });

        });

    });

});
