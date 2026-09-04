(function () {
    if (window.location.pathname !== '/' && window.location.pathname !== '') {
        return;
    }


    const TARGET_TERMS = {
        tattoo: ['татуировка', 'тату', 'tattoo'],
        paintings: ['картины', 'картина', 'painting'],
        merch: ['мерч', 'merch'],
        japanese: ['японская', 'япония', 'ирезуми'],
        graphics: ['графика'],
        engraving: ['гравюра'],
        traditional: ['традиционная', 'traditional', 'олдскул', 'old school'],
        dotwork: ['дотворк', 'dotwork'],
        free_sketch: ['свободные эскизы', 'свободный эскиз', 'эскизы'],
        canvas: ['холст', 'холстах'],
        skateboards: ['скейт', 'скейтах', 'скейтборд'],
        plywood: ['фанера', 'фанере']
    };

    function cardMatchesTarget(card, targetKey) {
        if (!targetKey) return false;

        const terms = TARGET_TERMS[targetKey] || [];
        const text = (card.textContent || '').toLowerCase();

        return terms.some(function (term) {
            return text.includes(term);
        });
    }

    function findCardForTarget(cards, targetKey) {
        if (!targetKey) return null;

        return cards.find(function (card) {
            return cardMatchesTarget(card, targetKey);
        }) || null;
    }

    function installStyles() {
        if (document.getElementById('homeCarouselMediaStyles')) return;

        const style = document.createElement('style');
        style.id = 'homeCarouselMediaStyles';

        style.textContent = `
            .home-carousel-card-with-admin-media {
                position: relative !important;
                overflow: hidden !important;
                isolation: isolate !important;
            }

            .home-carousel-card-with-admin-media > *:not(.home-carousel-admin-media) {
                position: relative !important;
                z-index: 2 !important;
            }

            .home-carousel-admin-media {
                position: absolute !important;
                inset: 0 !important;
                z-index: 0 !important;
                pointer-events: none !important;
                overflow: hidden !important;
                border-radius: inherit !important;
                opacity: 0.48 !important;
                background: rgba(0,0,0,0.35) !important;
            }

            .home-carousel-admin-media::after {
                content: "" !important;
                position: absolute !important;
                inset: 0 !important;
                z-index: 2 !important;
                background:
                    radial-gradient(circle at center, rgba(201, 163, 58, 0.08), transparent 44%),
                    linear-gradient(180deg, rgba(0,0,0,0.18), rgba(0,0,0,0.66)) !important;
            }

            .home-carousel-admin-media img,
            .home-carousel-admin-media video {
                position: absolute !important;
                inset: 0 !important;
                width: 100% !important;
                height: 100% !important;
                object-fit: cover !important;
                object-position: center center !important;
                filter:
                    brightness(0.82)
                    contrast(1.16)
                    saturate(1.04) !important;
                transform: scale(1.04) !important;
            }

            .home-carousel-admin-media--model {
                display: grid !important;
                place-items: center !important;
                color: rgba(242, 217, 132, 0.78) !important;
                font-family: Georgia, "Times New Roman", serif !important;
                font-size: 22px !important;
                letter-spacing: 0.10em !important;
                text-transform: uppercase !important;
                text-align: center !important;
                background:
                    radial-gradient(circle at center, rgba(201, 163, 58, 0.12), transparent 44%),
                    rgba(0,0,0,0.54) !important;
            }

            .home-carousel-card-with-admin-media:hover .home-carousel-admin-media {
                opacity: 0.64 !important;
            }

            .home-carousel-card-with-admin-media:hover .home-carousel-admin-media img,
            .home-carousel-card-with-admin-media:hover .home-carousel-admin-media video {
                transform: scale(1.08) !important;
            }
        `;

        document.head.appendChild(style);
    }

    function isVisible(el) {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);

        return (
            rect.width > 120 &&
            rect.height > 120 &&
            style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            parseFloat(style.opacity || '1') > 0
        );
    }

    function uniqueElements(elements) {
        return Array.from(new Set(elements));
    }

    function findCarouselCards() {
        const main = document.querySelector('main') || document.body;

        const selectors = [
            '[data-home-carousel-card]',
            '[data-carousel-card]',
            '.home-carousel-card',
            '.carousel-card',
            '.deck-card',
            '.skate-card',
            '.service-card',
            '.category-card',
            '.main-card',
            '.home-card'
        ];

        let cards = [];

        selectors.forEach(function (selector) {
            cards = cards.concat(Array.from(main.querySelectorAll(selector)));
        });

        cards = uniqueElements(cards)
            .filter(isVisible)
            .filter(function (el) {
                return !el.closest('header') &&
                    !el.closest('footer') &&
                    !el.closest('.work-cities') &&
                    !el.closest('.city-grid') &&
                    !el.closest('.video-sound-toggle') &&
                    !el.closest('.site-funnel-cta');
            });

        if (cards.length) {
            return cards;
        }

        /*
            Резервный режим: ищем крупные карточки на главной по тексту.
            Нужен на случай, если у текущей карусели нестандартные классы.
        */
        const terms = [
            'тату',
            'татуировка',
            'картины',
            'картина',
            'мерч',
            'эскиз',
            'японская',
            'графика',
            'гравюра',
            'дотворк'
        ];

        const candidates = Array.from(main.querySelectorAll('a, article, section > div, div'))
            .filter(isVisible)
            .filter(function (el) {
                const text = (el.textContent || '').trim().toLowerCase();

                if (!text) return false;

                return terms.some(function (term) {
                    return text.includes(term);
                });
            })
            .filter(function (el) {
                const rect = el.getBoundingClientRect();

                return (
                    rect.width < window.innerWidth * 0.92 &&
                    rect.height < window.innerHeight * 0.85 &&
                    !el.closest('header') &&
                    !el.closest('footer') &&
                    !el.closest('.work-cities') &&
                    !el.closest('.city-grid')
                );
            });

        /*
            Убираем вложенные элементы, оставляем более крупные карточки.
        */
        return uniqueElements(candidates).filter(function (el) {
            return !candidates.some(function (other) {
                return other !== el &&
                    other.contains(el) &&
                    other.getBoundingClientRect().width >= el.getBoundingClientRect().width;
            });
        });
    }

    function createMediaLayer(media) {
        const layer = document.createElement('div');
        layer.className = 'home-carousel-admin-media';

        if (media.media_type === 'image') {
            const img = document.createElement('img');
            img.src = media.file_path;
            img.alt = media.alt_text || media.title || '';
            layer.appendChild(img);
            return layer;
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
            layer.appendChild(video);

            layer._carouselVideo = video;

            return layer;
        }

        if (media.media_type === 'model') {
            layer.classList.add('home-carousel-admin-media--model');

            if (media.poster_path) {
                const img = document.createElement('img');
                img.src = media.poster_path;
                img.alt = media.alt_text || media.title || '3D модель';
                layer.appendChild(img);
            } else {
                layer.textContent = '3D';
            }

            return layer;
        }

        return layer;
    }

    function applyMediaToCards(media) {
        if (!media || !media.length) return;

        installStyles();

        const cards = findCarouselCards();

        if (!cards.length) {
            return;
        }

        const usedCards = new Set();

        media.forEach(function (item, index) {
            let card = null;

            if (item.target_key) {
                card = findCardForTarget(cards, item.target_key);
            }

            if (!card) {
                card = cards.find(function (candidate) {
                    return !usedCards.has(candidate);
                });
            }

            if (!card) return;
            if (card.dataset.homeCarouselMediaInstalled === '1') return;

            usedCards.add(card);

            const layer = createMediaLayer(item);

            card.classList.add('home-carousel-card-with-admin-media');
            card.dataset.homeCarouselMediaInstalled = '1';
            card.insertBefore(layer, card.firstChild);

            if (layer._carouselVideo) {
                const video = layer._carouselVideo;

                card.addEventListener('mouseenter', function () {
                    video.play().catch(function () {});
                });

                card.addEventListener('mouseleave', function () {
                    video.pause();
                });
            }
        });
    }

    fetch('/api/home-carousel')
        .then(function (response) {
            if (!response.ok) throw new Error('home carousel api error');
            return response.json();
        })
        .then(function (data) {
            applyMediaToCards(data.media || []);
        })
        .catch(function () {});
})();
