// === ArtToSlipAway home premium carousel polish ===
        document.addEventListener('DOMContentLoaded', function () {
            let cards = Array.from(document.querySelectorAll('.main-card'));
            if (!cards.length) return;

            const carousel = cards[0].parentElement;
            if (!carousel) return;

            carousel.classList.add('home-card-carousel');

            function detectCardType(card) {
                const text = card.innerText.toLowerCase();
                const links = Array.from(card.querySelectorAll('a')).map(a => a.href.toLowerCase()).join(' ');

                if (
                    links.includes('paintings') ||
                    text.includes('картины') ||
                    text.includes('холст') ||
                    text.includes('скейтборд') ||
                    text.includes('фанер')
                ) return 'paintings';

                if (
                    links.includes('tattoo-gift-certificate') ||
                    links.includes('stickerpack') ||
                    links.includes('tattoo-aftercare-kit') ||
                    links.includes('tshirts') ||
                    text.includes('сертификат') ||
                    text.includes('стикерпак') ||
                    text.includes('заживлен') ||
                    text.includes('футбол')
                ) return 'products';

                if (
                    links.includes('tattoo') ||
                    text.includes('тату')
                ) return 'tattoo';

                return 'other';
            }

            const priority = {
                paintings: 1,
                tattoo: 2,
                products: 3,
                other: 4
            };

            cards
                .slice()
                .sort(function (a, b) {
                    return priority[detectCardType(a)] - priority[detectCardType(b)];
                })
                .forEach(function (card) {
                    carousel.appendChild(card);
                });

            cards = Array.from(carousel.querySelectorAll('.main-card'));

            let activeIndex = Math.max(0, cards.findIndex(card => detectCardType(card) === 'tattoo'));
            let scrollTimer = null;
            let isProgrammaticScroll = false;

            function getClosestIndex() {
                const center = carousel.scrollLeft + carousel.clientWidth / 2;
                let closestIndex = activeIndex;
                let closestDistance = Infinity;

                cards.forEach(function (card, index) {
                    const cardCenter = card.offsetLeft + card.offsetWidth / 2;
                    const distance = Math.abs(center - cardCenter);

                    if (distance < closestDistance) {
                        closestDistance = distance;
                        closestIndex = index;
                    }
                });

                return closestIndex;
            }

            function updateCards() {
                activeIndex = getClosestIndex();
                const center = carousel.scrollLeft + carousel.clientWidth / 2;

                cards.forEach(function (card, index) {
                    const cardCenter = card.offsetLeft + card.offsetWidth / 2;
                    const distance = Math.abs(center - cardCenter);

                    card.classList.remove('is-active', 'is-near', 'is-left', 'is-right');

                    if (index === activeIndex) {
                        card.classList.add('is-active');
                        return;
                    }

                    if (cardCenter < center) {
                        card.classList.add('is-left');
                    } else {
                        card.classList.add('is-right');
                    }

                    if (distance < card.offsetWidth * 1.55) {
                        card.classList.add('is-near');
                    }
                });
            }

            function centerCard(index, behavior = 'smooth') {
                const card = cards[index];
                if (!card) return;

                const left = card.offsetLeft - carousel.clientWidth / 2 + card.offsetWidth / 2;

                isProgrammaticScroll = true;

                carousel.scrollTo({
                    left: left,
                    behavior: behavior
                });

                setTimeout(function () {
                    updateCards();
                    isProgrammaticScroll = false;
                }, 420);
            }

            function snapNearestCard() {
                const nearest = getClosestIndex();
                centerCard(nearest, 'smooth');
            }

            const oldArrows = document.querySelector('.home-carousel-arrows');
            if (oldArrows) oldArrows.remove();

            const arrows = document.createElement('div');
            arrows.className = 'home-carousel-arrows';
            arrows.innerHTML = `
                <button type="button" class="home-carousel-arrow" aria-label="Предыдущая карточка">‹</button>
                <button type="button" class="home-carousel-arrow" aria-label="Следующая карточка">›</button>
            `;

            carousel.insertAdjacentElement('afterend', arrows);

            const buttons = arrows.querySelectorAll('.home-carousel-arrow');

            /* ATS_CAROUSEL_ARROWS_SYNC_V1 */
            buttons[0].addEventListener('click', function () {
                /*
                 * Перед переключением заново получаем карточки
                 * и фактическую центральную позицию.
                 */
                cards = Array.from(
                    carousel.querySelectorAll('.main-card')
                );

                activeIndex = getClosestIndex();

                centerCard(
                    Math.max(
                        0,
                        activeIndex - 1
                    )
                );
            });

            buttons[1].addEventListener('click', function () {
                /*
                 * Не используем устаревший activeIndex:
                 * вычисляем его непосредственно перед кликом.
                 */
                cards = Array.from(
                    carousel.querySelectorAll('.main-card')
                );

                activeIndex = getClosestIndex();

                centerCard(
                    Math.min(
                        cards.length - 1,
                        activeIndex + 1
                    )
                );
            });

            carousel.addEventListener('scroll', function () {
                updateCards();

                if (isProgrammaticScroll) return;

                clearTimeout(scrollTimer);
                scrollTimer = setTimeout(function () {
                    snapNearestCard();
                }, 180);
            });

            // Вертикальный скролл страницы не трогаем.
            // Вбок колесом — только Shift + колесо / тачпад.
            carousel.addEventListener('wheel', function (event) {
                if (!event.shiftKey) return;

                event.preventDefault();
                carousel.scrollLeft += event.deltaY || event.deltaX;
            }, { passive: false });

            let isDown = false;
            let startX = 0;
            let startScrollLeft = 0;
            let hasDragged = false;

            carousel.addEventListener('mousedown', function (event) {
                isDown = true;
                hasDragged = false;
                startX = event.pageX;
                startScrollLeft = carousel.scrollLeft;
                carousel.classList.add('dragging');
            });

            window.addEventListener('mouseup', function () {
                if (isDown) {
                    isDown = false;
                    carousel.classList.remove('dragging');
                    setTimeout(snapNearestCard, 80);
                }
            });

            carousel.addEventListener('mousemove', function (event) {
                if (!isDown) return;

                event.preventDefault();

                const distance = event.pageX - startX;

                if (Math.abs(distance) > 5) {
                    hasDragged = true;
                }

                carousel.scrollLeft = startScrollLeft - distance;
            });

            carousel.addEventListener('click', function (event) {
                /*
                 * ATS_BOARD_DIRECT_LINKS_V1
                 * Нажатие на название раздела сразу открывает ссылку,
                 * даже если доска сейчас боковая.
                 */
                const directLink =
                    event.target.closest(
                        'a.subcard[href], a.button[href]'
                    );

                if (directLink) {
                    return;
                }

                const card = event.target.closest('.main-card');
                if (!card) return;

                const index = cards.indexOf(card);

                if (hasDragged) {
                    event.preventDefault();
                    event.stopPropagation();
                    hasDragged = false;
                    return;
                }

                if (!card.classList.contains('is-active')) {
                    event.preventDefault();
                    event.stopPropagation();
                    centerCard(index);
                }
            }, true);

            window.addEventListener('resize', function () {
                updateCards();
                centerCard(activeIndex, 'auto');
            });

            setTimeout(function () {
                const tattooIndex = Math.max(0, cards.findIndex(card => detectCardType(card) === 'tattoo'));
                activeIndex = tattooIndex;
                centerCard(tattooIndex, 'auto');
                updateCards();
            }, 180);
        });
