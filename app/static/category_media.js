(function () {
    const path = window.location.pathname;

    if (!path.startsWith('/categories/')) {
        return;
    }

    const slug = decodeURIComponent(path.replace('/categories/', '').replace(/^\/+|\/+$/g, ''));

    if (!slug) return;

    const isFreeSketches = ['free-sketches', 'free_sketch', 'free-sketch'].includes(slug);


    // ATS_FREE_LOGO_FLASH_FIX_V1
// ATS_FREE_SKETCH_HEADER_LOGO_V1
    if (isFreeSketches) {

        const logoStyle =
            document.createElement('style');

        logoStyle.id =
            'atsFreeSketchHeaderLogoV1';

        logoStyle.textContent = `
            .ats-free-header-logo {
                display: inline-flex;
                align-items: center;
                justify-content: flex-start;
                width: auto;
                text-decoration: none;
            }

            .ats-free-header-logo img {
                display: block;
                width: auto;
                height: 42px;
                max-width: 210px;
                object-fit: contain;

                filter:
                    drop-shadow(
                        0 0 8px
                        rgba(201, 163, 58, .18)
                    );

                transition:
                    transform 180ms ease,
                    filter 180ms ease;
            }

            .ats-free-header-logo:hover img {
                transform:
                    translateY(-1px);

                filter:
                    drop-shadow(
                        0 0 9px
                        rgba(242, 217, 132, .45)
                    )
                    drop-shadow(
                        0 0 18px
                        rgba(201, 163, 58, .18)
                    );
            }

            @media (max-width: 720px) {
                .ats-free-header-logo img {
                    height: 36px;
                    max-width: 175px;
                }
            }
        `;

        document.head.appendChild(
            logoStyle
        );


        function installFreeSketchLogo() {

            const candidates =
                Array.from(
                    document.querySelectorAll(
                        'header a, nav a'
                    )
                );

            const logoLink =
                candidates.find(
                    function (link) {

                        const text =
                            (
                                link.textContent ||
                                ''
                            )
                            .replace(
                                /\s+/g,
                                ' '
                            )
                            .trim()
                            .toLowerCase();

                        return (
                            text ===
                            'arttoslipaway'
                        );
                    }
                );

            if (
                !logoLink ||
                logoLink.dataset.atsLogoInstalled
            ) {
                return;
            }

            logoLink.dataset.atsLogoInstalled =
                '1';

            logoLink.classList.add(
                'ats-free-header-logo'
            );

            logoLink.textContent = '';

            const img =
                document.createElement('img');

            img.src =
                '/static/images/logo.webp?v=20260815-logo-webp';

            img.alt =
                'ArtToSlipAway';

            img.decoding =
                'async';

            logoLink.appendChild(
                img
            );
        }


        if (
            document.readyState ===
            'loading'
        ) {
            document.addEventListener(
                'DOMContentLoaded',
                installFreeSketchLogo,
                {
                    once: true
                }
            );
        } else {
            installFreeSketchLogo();
        }
    }



    // ATS_FREE_SKETCH_CAROUSEL_VISUAL_V2
    if (isFreeSketches) {

        const visualStyle =
            document.createElement('style');

        visualStyle.id =
            'atsFreeSketchCarouselVisualV2';

        visualStyle.textContent = `

            body.category-free-sketches-page
            .free-sketches-carousel-section {
                box-sizing: border-box !important;
                max-width: 1280px !important;
                margin: 6px auto 30px !important;
                padding: 0 54px !important;
                position: relative !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-head {
                box-sizing: border-box !important;
                margin-bottom: 12px !important;
                padding: 0 64px !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-title {
                margin: 0 !important;
                font-size:
                    clamp(36px, 3.1vw, 48px) !important;
                line-height: .96 !important;
                letter-spacing: .035em !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-subtitle {
                max-width: 590px !important;
                margin-top: 9px !important;
                font-size: 14px !important;
                line-height: 1.4 !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-track {
                box-sizing: border-box !important;

                grid-auto-columns:
                    minmax(360px, 400px) !important;

                gap: 26px !important;

                align-items: start !important;

                padding:
                    4px
                    calc((100% - 400px) / 2)
                    12px !important;

                scroll-padding-inline:
                    calc((100% - 400px) / 2) !important;

                scroll-snap-type:
                    x mandatory !important;

                scroll-behavior:
                    auto !important;

                scrollbar-width:
                    none !important;

                -webkit-mask-image:
                    linear-gradient(
                        90deg,
                        transparent 0%,
                        #000 8%,
                        #000 92%,
                        transparent 100%
                    );

                mask-image:
                    linear-gradient(
                        90deg,
                        transparent 0%,
                        #000 8%,
                        #000 92%,
                        transparent 100%
                    );
            }

            body.category-free-sketches-page
            .free-sketches-carousel-track::-webkit-scrollbar {
                display: none !important;
            }

            body.category-free-sketches-page
            .free-sketch-card {
                box-sizing: border-box !important;

                width: 100% !important;
                min-width: 0 !important;
                min-height: 0 !important;

                padding: 0 !important;

                scroll-snap-align:
                    center !important;

                border-radius:
                    20px !important;

                overflow:
                    hidden !important;

                opacity: .30;

                transform:
                    scale(.92);

                transform-origin:
                    center center;

                filter:
                    brightness(.60)
                    saturate(.82);

                transition:
                    opacity 180ms ease,
                    transform 180ms ease,
                    filter 180ms ease;
            }

            body.category-free-sketches-page
            .free-sketch-card.is-carousel-active {
                opacity: 1 !important;
                transform: scale(1) !important;
                filter: none !important;
            }

            body.category-free-sketches-page
            .free-sketch-preview {
                box-sizing: border-box !important;

                height:
                    clamp(
                        300px,
                        37vh,
                        350px
                    ) !important;

                min-height: 0 !important;

                border-left: 0 !important;
                border-right: 0 !important;
                border-top: 0 !important;
            }

            body.category-free-sketches-page
            .free-sketch-name {
                margin: 0 !important;

                padding:
                    14px
                    17px
                    0 !important;

                font-size:
                    23px !important;

                line-height:
                    1.08 !important;
            }

            body.category-free-sketches-page
            .free-sketch-meta {
                margin:
                    7px
                    0
                    12px !important;

                padding:
                    0
                    17px !important;

                font-size:
                    12px !important;

                line-height:
                    1.36 !important;
            }

            body.category-free-sketches-page
            .free-sketch-cta {
                align-self:
                    flex-start !important;

                width:
                    auto !important;

                min-height:
                    38px !important;

                margin:
                    auto
                    17px
                    16px !important;

                padding:
                    9px
                    15px !important;

                border-radius:
                    999px !important;

                font-size:
                    10px !important;
            }

            body.category-free-sketches-page
            .ats-free-model-open {
                left:
                    14px !important;

                bottom:
                    14px !important;

                min-height:
                    34px !important;

                padding:
                    8px
                    12px !important;

                font-size:
                    9px !important;
            }

            body.category-free-sketches-page
            .ats-free-model-hint {
                top:
                    13px !important;

                left:
                    13px !important;

                padding:
                    8px
                    10px !important;

                font-size:
                    9px !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-controls {
                position:
                    absolute !important;

                left:
                    8px !important;

                right:
                    8px !important;

                top:
                    57% !important;

                z-index:
                    50 !important;

                display:
                    flex !important;

                justify-content:
                    space-between !important;

                width:
                    auto !important;

                pointer-events:
                    none !important;

                transform:
                    translateY(-50%) !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-button {
                width:
                    46px !important;

                height:
                    46px !important;

                flex:
                    0 0 46px !important;

                pointer-events:
                    auto !important;

                background:
                    rgba(
                        5,
                        5,
                        5,
                        .88
                    ) !important;

                backdrop-filter:
                    blur(12px);

                transition:
                    transform 130ms ease,
                    background 130ms ease,
                    border-color 130ms ease !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-button:hover {
                transform:
                    scale(1.08) !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-button:active {
                transform:
                    scale(.93) !important;
            }

            @media
            (max-height: 820px)
            and
            (min-width: 721px) {

                body.category-free-sketches-page
                .free-sketch-preview {
                    height:
                        clamp(
                            265px,
                            34vh,
                            305px
                        ) !important;
                }

                body.category-free-sketches-page
                .free-sketches-carousel-title {
                    font-size:
                        36px !important;
                }

                body.category-free-sketches-page
                .free-sketches-carousel-head {
                    margin-bottom:
                        8px !important;
                }
            }

            @media
            (max-width: 720px) {

                body.category-free-sketches-page
                .free-sketches-carousel-section {
                    padding:
                        0
                        12px !important;
                }

                body.category-free-sketches-page
                .free-sketches-carousel-head {
                    padding:
                        0 !important;
                }

                body.category-free-sketches-page
                .free-sketches-carousel-track {
                    grid-auto-columns:
                        84vw !important;

                    gap:
                        18px !important;

                    padding:
                        4px
                        8vw
                        12px !important;

                    scroll-padding-inline:
                        8vw !important;

                    -webkit-mask-image:
                        none;

                    mask-image:
                        none;
                }

                body.category-free-sketches-page
                .free-sketch-preview {
                    height:
                        min(
                            47vh,
                            350px
                        ) !important;
                }

                body.category-free-sketches-page
                .free-sketches-carousel-controls {
                    left:
                        1px !important;

                    right:
                        1px !important;

                    top:
                        56% !important;
                }

                body.category-free-sketches-page
                .free-sketches-carousel-button {
                    width:
                        40px !important;

                    height:
                        40px !important;

                    flex-basis:
                        40px !important;
                }
            }
        `;

        document.head.appendChild(
            visualStyle
        );


        function installActiveCardState(track) {

            if (
                !track ||
                track.dataset.atsVisualV2
            ) {
                return;
            }

            track.dataset.atsVisualV2 =
                '1';

            let raf = 0;


            function updateActiveCard() {

                raf = 0;

                const cards =
                    Array.from(
                        track.querySelectorAll(
                            '.free-sketch-card'
                        )
                    );

                if (!cards.length) {
                    return;
                }

                const trackRect =
                    track.getBoundingClientRect();

                const center =
                    trackRect.left +
                    trackRect.width / 2;

                let activeCard = null;
                let bestDistance = Infinity;


                cards.forEach(
                    function (card) {

                        const rect =
                            card.getBoundingClientRect();

                        const cardCenter =
                            rect.left +
                            rect.width / 2;

                        const distance =
                            Math.abs(
                                center -
                                cardCenter
                            );

                        if (
                            distance <
                            bestDistance
                        ) {
                            bestDistance =
                                distance;

                            activeCard =
                                card;
                        }
                    }
                );


                cards.forEach(
                    function (card) {

                        card.classList.toggle(
                            'is-carousel-active',
                            card === activeCard
                        );
                    }
                );
            }


            track.addEventListener(
                'scroll',
                function () {

                    if (raf) {
                        return;
                    }

                    raf =
                        requestAnimationFrame(
                            updateActiveCard
                        );
                },
                {
                    passive: true
                }
            );


            requestAnimationFrame(
                updateActiveCard
            );
        }


        function scanFreeSketchCarousels() {

            document
                .querySelectorAll(
                    '.free-sketches-carousel-track'
                )
                .forEach(
                    installActiveCardState
                );
        }


        if (
            document.readyState ===
            'loading'
        ) {
            document.addEventListener(
                'DOMContentLoaded',
                scanFreeSketchCarousels,
                {
                    once: true
                }
            );
        } else {
            scanFreeSketchCarousels();
        }


        new MutationObserver(
            scanFreeSketchCarousels
        ).observe(
            document.body,
            {
                childList: true,
                subtree: true
            }
        );
    }



    // ATS_FREE_SKETCH_VIEWPORT_CAROUSEL_V1
    if (isFreeSketches) {

        /*
         * Компактная карточка:
         * должна помещаться в обычный viewport целиком.
         */
        const viewportStyle = document.createElement('style');

        viewportStyle.id =
            'atsFreeSketchViewportCarouselV1';

        viewportStyle.textContent = `
            body.category-free-sketches-page
            .free-sketches-carousel-section {
                margin-top: 22px !important;
                margin-bottom: 42px !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-head {
                margin-bottom: 14px !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-title {
                font-size:
                    clamp(34px, 3.4vw, 46px) !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-track {
                grid-auto-columns:
                    minmax(300px, 360px) !important;

                gap: 20px !important;

                scroll-behavior: auto !important;

                padding-top: 4px !important;
                padding-bottom: 12px !important;
            }

            body.category-free-sketches-page
            .free-sketch-card {
                min-height: 0 !important;
            }

            body.category-free-sketches-page
            .free-sketch-preview {
                height:
                    clamp(
                        330px,
                        46vh,
                        420px
                    ) !important;

                min-height: 0 !important;
            }

            body.category-free-sketches-page
            .free-sketch-name {
                padding:
                    16px 18px 0 !important;

                font-size: 25px !important;
            }

            body.category-free-sketches-page
            .free-sketch-meta {
                margin:
                    7px 0 14px !important;

                padding:
                    0 18px !important;

                font-size: 13px !important;
                line-height: 1.4 !important;
            }

            body.category-free-sketches-page
            .free-sketch-cta {
                min-height: 40px !important;

                margin:
                    auto 18px 18px !important;

                padding:
                    10px 15px !important;
            }

            body.category-free-sketches-page
            .ats-free-model-open {
                left: 14px !important;
                bottom: 14px !important;
            }

            body.category-free-sketches-page
            .ats-free-model-hint {
                top: 14px !important;
                left: 14px !important;
            }

            @media (max-height: 800px)
                   and (min-width: 721px) {

                body.category-free-sketches-page
                .free-sketch-preview {
                    height:
                        clamp(
                            300px,
                            42vh,
                            350px
                        ) !important;
                }

                body.category-free-sketches-page
                .free-sketches-carousel-title {
                    font-size:
                        clamp(
                            30px,
                            3vw,
                            40px
                        ) !important;
                }
            }

            @media (max-width: 720px) {

                body.category-free-sketches-page
                .free-sketches-carousel-track {
                    grid-auto-columns:
                        minmax(
                            270px,
                            84vw
                        ) !important;
                }

                body.category-free-sketches-page
                .free-sketch-preview {
                    height:
                        clamp(
                            330px,
                            52vh,
                            390px
                        ) !important;
                }
            }
        `;

        document.head.appendChild(
            viewportStyle
        );


        /*
         * На общей странице свободных эскизов
         * ссылка "На главную" не нужна.
         */
        const hideBackHomeLink = function () {
            document
                .querySelectorAll('a')
                .forEach(function (link) {
                    const label =
                        (link.textContent || '')
                            .replace(/\s+/g, ' ')
                            .trim()
                            .toLowerCase();

                    if (
                        label === '← на главную' ||
                        label === 'на главную'
                    ) {
                        link.style.display = 'none';
                    }
                });
        };

        if (document.readyState === 'loading') {
            document.addEventListener(
                'DOMContentLoaded',
                hideBackHomeLink,
                { once: true }
            );
        } else {
            hideBackHomeLink();
        }


        /*
         * Своя короткая анимация стрелок.
         * Старый click-handler блокируем в capture phase,
         * поэтому двойного перелистывания не будет.
         */
        const carouselAnimations =
            new WeakMap();

        function animateCarousel(
            track,
            target
        ) {
            const previous =
                carouselAnimations.get(track);

            if (previous) {
                cancelAnimationFrame(previous);
            }

            const start =
                track.scrollLeft;

            const max =
                Math.max(
                    0,
                    track.scrollWidth -
                    track.clientWidth
                );

            const end =
                Math.max(
                    0,
                    Math.min(target, max)
                );

            const distance =
                end - start;

            if (Math.abs(distance) < 2) {
                return;
            }

            const duration = 160;
            const started = performance.now();

            function frame(now) {
                const progress =
                    Math.min(
                        1,
                        (now - started) /
                        duration
                    );

                /*
                 * easeOutCubic:
                 * быстрый старт, мягкая остановка.
                 */
                const eased =
                    1 -
                    Math.pow(
                        1 - progress,
                        3
                    );

                track.scrollLeft =
                    start +
                    distance * eased;

                if (progress < 1) {
                    const raf =
                        requestAnimationFrame(
                            frame
                        );

                    carouselAnimations.set(
                        track,
                        raf
                    );
                } else {
                    carouselAnimations.delete(
                        track
                    );
                }
            }

            const raf =
                requestAnimationFrame(frame);

            carouselAnimations.set(
                track,
                raf
            );
        }


        document.addEventListener(
            'click',
            function (event) {
                const button =
                    event.target.closest(
                        '.free-sketches-carousel-button'
                    );

                if (!button) {
                    return;
                }

                const controls =
                    button.closest(
                        '.free-sketches-carousel-controls'
                    );

                const section =
                    button.closest(
                        '.free-sketches-carousel-section'
                    );

                if (!controls || !section) {
                    return;
                }

                const track =
                    section.querySelector(
                        '.free-sketches-carousel-track'
                    );

                if (!track) {
                    return;
                }

                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();

                const buttons =
                    Array.from(
                        controls.querySelectorAll(
                            '.free-sketches-carousel-button'
                        )
                    );

                const direction =
                    buttons.indexOf(button) === 0
                        ? -1
                        : 1;

                const card =
                    track.querySelector(
                        '.free-sketch-card'
                    );

                if (!card) {
                    return;
                }

                const css =
                    getComputedStyle(track);

                const gap =
                    parseFloat(
                        css.columnGap ||
                        css.gap ||
                        '20'
                    ) || 20;

                const step =
                    card.getBoundingClientRect()
                        .width +
                    gap;

                animateCarousel(
                    track,
                    track.scrollLeft +
                    direction * step
                );
            },
            true
        );
    }



    // ATS_FREE_MODEL_SINGLE_INLINE_FLOW_V2
    if (isFreeSketches) {
        document.addEventListener(
            'click',
            function (event) {
                const stage = event.target.closest(
                    '.ats-free-model-stage'
                );

                if (!stage) {
                    return;
                }

                /*
                 * Сама inline-кнопка имеет
                 * собственный обработчик.
                 */
                if (
                    event.target.closest(
                        '.ats-free-model-open'
                    )
                ) {
                    return;
                }

                /*
                 * После открытия model-viewer
                 * должен получать управление мышью.
                 * Его собственные listeners уже
                 * блокируют всплытие к карточке.
                 */
                if (
                    event.target.closest(
                        'model-viewer'
                    )
                ) {
                    return;
                }

                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();

                const button =
                    stage.querySelector(
                        '.ats-free-model-open'
                    );

                if (
                    button &&
                    !button.disabled
                ) {
                    button.click();
                }
            },
            true
        );
    }



    // ATS_FREE_SKETCH_JAPANESE_CARD_V1
    if (
        isFreeSketches &&
        !document.getElementById('atsFreeSketchJapaneseCardV1')
    ) {
        const style = document.createElement('style');

        style.id = 'atsFreeSketchJapaneseCardV1';

        style.textContent = `
            body.category-free-sketches-page
            .free-sketches-carousel-track {
                grid-auto-columns: minmax(300px, 390px);
                gap: 24px;
                align-items: stretch;
            }

            body.category-free-sketches-page
            .free-sketch-card {
                box-sizing: border-box;
                min-height: 0;
                padding: 0;
                overflow: hidden;

                border:
                    1px solid rgba(201, 163, 58, 0.54);
                border-radius: 22px;

                background:
                    linear-gradient(
                        180deg,
                        rgba(26, 24, 20, 0.94),
                        rgba(6, 6, 6, 0.98)
                    );

                box-shadow:
                    0 20px 54px rgba(0, 0, 0, 0.42),
                    0 0 24px rgba(201, 163, 58, 0.10);
            }

            body.category-free-sketches-page
            .free-sketch-preview {
                position: relative;
                display: block;

                width: 100%;
                height: 500px;
                min-height: 500px;

                padding: 0;
                overflow: hidden;

                border: 0;
                border-bottom:
                    1px solid rgba(201, 163, 58, 0.28);

                background:
                    radial-gradient(
                        circle at 50% 42%,
                        rgba(201, 163, 58, 0.13),
                        transparent 34%
                    ),
                    radial-gradient(
                        circle at center,
                        #24201a 0%,
                        #070707 72%
                    );

                isolation: isolate;
            }

            body.category-free-sketches-page
            .free-sketch-preview > img,
            body.category-free-sketches-page
            .free-sketch-preview > video {
                display: block;
                width: 100%;
                height: 100%;
                object-fit: cover;
                object-position: center;
                background: #070707;
            }

            body.category-free-sketches-page
            .free-sketch-name {
                margin: 0;
                padding: 20px 20px 0;

                color: #f2d984;
                font-family:
                    Georgia,
                    "Times New Roman",
                    serif;
                font-size: 26px;
                font-weight: 400;
                line-height: 1.15;
            }

            body.category-free-sketches-page
            .free-sketch-meta {
                margin: 10px 0 18px;
                padding: 0 20px;

                color: rgba(232, 221, 198, 0.68);
                font-family: Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
            }

            body.category-free-sketches-page
            .free-sketch-cta {
                align-self: flex-start;

                min-height: 44px;
                margin: auto 20px 20px;
                padding: 11px 16px;

                border: 1px solid #c9a33a;
                border-radius: 999px;

                background: #c9a33a;
                color: #111;

                font-family: Arial, sans-serif;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.07em;
            }

            body.category-free-sketches-page
            .free-sketch-cta:hover {
                border-color: #f2d984;
                background: #f2d984;

                box-shadow:
                    0 0 20px
                    rgba(201, 163, 58, 0.36);
            }

            /*
             * Живая 3D-модель находится под WebP-превью.
             */
            body.category-free-sketches-page
            .ats-free-model-viewer {
                position: absolute;
                inset: 0;
                z-index: 5;

                display: block;
                width: 100%;
                height: 100%;

                border: 0;
                outline: 0;

                background: #070707;
                cursor: grab;

                --poster-color: #070707;
                --progress-bar-color: #d7af38;
            }

            body.category-free-sketches-page
            .ats-free-model-viewer:active {
                cursor: grabbing;
            }

            /*
             * Чистый WebP-постер поверх model-viewer.
             */
            body.category-free-sketches-page
            .ats-free-model-poster {
                position: absolute;
                inset: 0;
                z-index: 20;

                display: block;
                width: 100%;
                height: 100%;

                object-fit: cover;
                object-position: center;

                background: #070707;

                opacity: 1;
                visibility: visible;

                transition:
                    opacity 180ms ease,
                    visibility 180ms ease;
            }

            body.category-free-sketches-page
            .free-sketch-preview.is-3d-open
            .ats-free-model-poster {
                opacity: 0;
                visibility: hidden;
                pointer-events: none;
            }

            body.category-free-sketches-page
            .ats-free-model-open {
                position: absolute;
                left: 18px;
                bottom: 18px;
                z-index: 40;

                display: inline-flex;
                align-items: center;
                justify-content: center;

                min-height: 38px;
                padding: 9px 13px;

                border:
                    1px solid rgba(201, 163, 58, 0.72);
                border-radius: 999px;

                background: rgba(5, 5, 5, 0.88);
                color: #f2d984;

                font-family: Arial, sans-serif;
                font-size: 10px;
                font-weight: 700;
                line-height: 1;
                letter-spacing: 0.08em;
                text-transform: uppercase;

                cursor: pointer;
            }

            body.category-free-sketches-page
            .ats-free-model-open:hover {
                border-color: #f2d984;
                background: #f2d984;
                color: #111;
            }

            body.category-free-sketches-page
            .free-sketch-preview.is-3d-open
            .ats-free-model-open {
                display: none;
            }

            body.category-free-sketches-page
            .ats-free-model-hint {
                position: absolute;
                top: 16px;
                left: 16px;
                z-index: 30;

                display: none;

                padding: 9px 12px;

                border:
                    1px solid rgba(201, 163, 58, 0.38);
                border-radius: 999px;

                background: rgba(4, 4, 4, 0.68);
                color: rgba(242, 217, 132, 0.86);

                font-family: Arial, sans-serif;
                font-size: 10px;
                font-weight: 700;
                line-height: 1;
                letter-spacing: 0.08em;
                text-transform: uppercase;

                pointer-events: none;
                backdrop-filter: blur(12px);
            }

            body.category-free-sketches-page
            .free-sketch-preview.is-3d-open
            .ats-free-model-hint {
                display: inline-flex;
            }

            @media (max-width: 900px) {
                body.category-free-sketches-page
                .free-sketches-carousel-track {
                    grid-auto-columns:
                        minmax(280px, 82vw);
                }

                body.category-free-sketches-page
                .free-sketch-preview {
                    height: 430px;
                    min-height: 430px;
                }
            }

            @media (max-width: 560px) {
                body.category-free-sketches-page
                .free-sketch-card {
                    border-radius: 18px;
                }

                body.category-free-sketches-page
                .free-sketch-preview {
                    height: 390px;
                    min-height: 390px;
                }

                body.category-free-sketches-page
                .free-sketch-name {
                    padding:
                        17px 17px 0;
                    font-size: 24px;
                }

                body.category-free-sketches-page
                .free-sketch-meta {
                    padding: 0 17px;
                }

                body.category-free-sketches-page
                .free-sketch-cta {
                    margin:
                        auto 17px 17px;
                }
            }
        `;

        document.head.appendChild(style);
    }

    function installStyles() {
        if (document.getElementById('categoryMediaStyles')) return;

        const style = document.createElement('style');
        style.id = 'categoryMediaStyles';

        style.textContent = `
            body.category-free-sketches-page .old-examples-hidden {
                display: none !important;
            }

            .free-sketches-carousel-section {
                max-width: 1180px;
                margin: 36px auto 62px;
                padding: 0 24px;
                position: relative;
            }

            .free-sketches-carousel-head {
                display: flex;
                align-items: flex-end;
                justify-content: space-between;
                gap: 18px;
                margin-bottom: 20px;
            }

            .free-sketches-carousel-title {
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: clamp(30px, 4vw, 52px);
                line-height: 1;
                font-weight: 400;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                margin: 0;
            }

            .free-sketches-carousel-subtitle {
                color: rgba(232, 221, 198, 0.62);
                font-family: Arial, sans-serif;
                font-size: 15px;
                line-height: 1.45;
                max-width: 560px;
                margin-top: 10px;
            }

            .free-sketches-carousel-controls {
                display: flex;
                gap: 10px;
                flex-shrink: 0;
            }

            .free-sketches-carousel-button {
                width: 42px;
                height: 42px;
                border-radius: 999px;
                border: 1px solid rgba(201, 163, 58, 0.58);
                background: rgba(0,0,0,0.52);
                color: #c9a33a;
                cursor: pointer;
                font-size: 22px;
                line-height: 1;
                display: grid;
                place-items: center;
            }

            .free-sketches-carousel-button:hover {
                color: #111;
                background: #f2d984;
                border-color: #f2d984;
            }

            .free-sketches-carousel-track {
                display: grid;
                grid-auto-flow: column;
                grid-auto-columns: minmax(250px, 320px);
                gap: 18px;
                overflow-x: auto;
                overflow-y: hidden;
                scroll-snap-type: x mandatory;
                scroll-behavior: smooth;
                padding: 6px 4px 18px;
                scrollbar-width: thin;
            }

            .free-sketch-card {
                scroll-snap-align: start;
                border: 1px solid rgba(201, 163, 58, 0.36);
                background:
                    linear-gradient(180deg, rgba(0,0,0,0.48), rgba(0,0,0,0.86)),
                    radial-gradient(circle at center top, rgba(201, 163, 58, 0.07), transparent 44%);
                padding: 14px;
                min-height: 430px;
                display: flex;
                flex-direction: column;
                box-shadow:
                    0 0 24px rgba(0,0,0,0.34),
                    inset 0 0 18px rgba(201, 163, 58, 0.025);
            }

            .free-sketch-preview {
                width: 100%;
                height: 280px;
                border: 1px solid rgba(201, 163, 58, 0.22);
                background: rgba(0,0,0,0.56);
                overflow: hidden;
                display: grid;
                place-items: center;
            }

            .free-sketch-preview img,
            .free-sketch-preview video {
                width: 100%;
                height: 100%;
                object-fit: contain;
                display: block;
                background: rgba(0,0,0,0.42);
            }

            .free-sketch-name {
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 20px;
                line-height: 1.2;
                margin: 14px 0 8px;
            }

            .free-sketch-meta {
                color: rgba(232, 221, 198, 0.62);
                font-family: Arial, sans-serif;
                font-size: 13px;
                line-height: 1.4;
                margin-bottom: 14px;
            }

            .free-sketch-cta {
                margin-top: auto;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-height: 42px;
                padding: 12px 14px;
                border: 1px solid #c9a33a;
                background: #c9a33a;
                color: #111;
                text-decoration: none;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-family: Arial, sans-serif;
                font-size: 12px;
            }

            .free-sketch-cta:hover {
                background: #f2d984;
                border-color: #f2d984;
            }

            .category-media-section {
                max-width: 1180px;
                margin: 40px auto 80px;
                padding: 0 24px;
            }

            .category-media-title {
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: clamp(28px, 4vw, 48px);
                font-weight: 400;
                margin: 0 0 24px;
            }

            .category-media-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 18px;
            }

            .category-media-card {
                border: 1px solid rgba(201, 163, 58, 0.34);
                background: rgba(0,0,0,0.42);
                padding: 14px;
            }

            .category-media-preview {
                width: 100%;
                height: 300px;
                background: rgba(0,0,0,0.48);
                border: 1px solid rgba(201, 163, 58, 0.20);
                overflow: hidden;
                display: grid;
                place-items: center;
            }

            .category-media-preview img,
            .category-media-preview video {
                width: 100%;
                height: 100%;
                object-fit: contain;
                display: block;
            }

            .category-media-name {
                color: #f2d984;
                font-family: Georgia, "Times New Roman", serif;
                font-size: 20px;
                margin-top: 10px;
            }

            @media (max-width: 900px) {
                .free-sketches-carousel-head {
                    align-items: flex-start;
                    flex-direction: column;
                }

                .free-sketches-carousel-track {
                    grid-auto-columns: minmax(240px, 82vw);
                }

                .category-media-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }

            @media (max-width: 640px) {
                .free-sketches-carousel-section {
                    padding: 0 16px;
                }

                .free-sketch-preview {
                    height: 300px;
                }

                .category-media-grid {
                    grid-template-columns: 1fr;
                }
            }
        `;

        document.head.appendChild(style);

        if (!document.getElementById('free-sketch-lightbox-style')) {
            const lightboxStyle = document.createElement('style');
            lightboxStyle.id = 'free-sketch-lightbox-style';
            lightboxStyle.textContent = `
                .free-sketch-preview {
                    position: relative;
                    cursor: zoom-in;
                    overflow: hidden;
                }

                .free-sketch-preview--model-card img,
                .free-sketch-preview--video video {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }

                .free-sketch-model-placeholder {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    height: 100%;
                    min-height: 280px;
                    background: #050505;
                    color: #f2d984;
                    font-family: Arial, sans-serif;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                }

                .free-sketch-preview-badge {
                    position: absolute;
                    left: 14px;
                    bottom: 14px;
                    z-index: 3;
                    padding: 8px 11px;
                    border: 1px solid rgba(201, 163, 58, 0.55);
                    background: rgba(0, 0, 0, 0.72);
                    color: #f2d984;
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    line-height: 1;
                    letter-spacing: 0.06em;
                    text-transform: uppercase;
                    pointer-events: none;
                }

                .free-sketch-lightbox-open {
                    overflow: hidden;
                }

                .free-sketch-lightbox {
                    position: fixed;
                    inset: 0;
                    z-index: 99999;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 28px;
                    background: rgba(0, 0, 0, 0.88);
                    backdrop-filter: blur(10px);
                }

                .free-sketch-lightbox-panel {
                    position: relative;
                    width: min(1180px, 96vw);
                    max-height: 92vh;
                    display: grid;
                    grid-template-columns: minmax(0, 1fr) 320px;
                    gap: 22px;
                    border: 1px solid rgba(201, 163, 58, 0.45);
                    background: #050505;
                    box-shadow: 0 30px 90px rgba(0, 0, 0, 0.72);
                    padding: 22px;
                }

                .free-sketch-lightbox-close {
                    position: absolute;
                    top: 12px;
                    right: 12px;
                    z-index: 5;
                    width: 42px;
                    height: 42px;
                    border: 1px solid rgba(201, 163, 58, 0.7);
                    background: rgba(0, 0, 0, 0.72);
                    color: #f2d984;
                    font-size: 30px;
                    line-height: 1;
                    cursor: pointer;
                }

                .free-sketch-lightbox-close:hover {
                    background: #f2d984;
                    color: #111;
                }

                .free-sketch-lightbox-media {
                    position: relative;
                    min-height: 68vh;
                    max-height: 76vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    overflow: hidden;
                    background: radial-gradient(circle at center, #24201a 0%, #050505 68%);
                    border: 1px solid rgba(201, 163, 58, 0.22);
                }

                .free-sketch-lightbox-media img,
                .free-sketch-lightbox-media video {
                    max-width: 100%;
                    max-height: 76vh;
                    width: auto;
                    height: auto;
                    object-fit: contain;
                    display: block;
                }

                .free-sketch-lightbox-media model-viewer {
                    display: block;
                    width: 100%;
                    height: 76vh;
                    min-height: 560px;
                    background: transparent;
                    cursor: grab;
                    pointer-events: auto !important;
                }

                .free-sketch-lightbox-media model-viewer:active {
                    cursor: grabbing;
                }

                .free-sketch-lightbox-media--model {
                    isolation: isolate;
                    background:
                        radial-gradient(circle at 50% 42%, rgba(201, 163, 58, 0.14), transparent 34%),
                        radial-gradient(circle at center, #17140f 0%, #050505 72%);
                }

                .free-sketch-lightbox-media--model::before {
                    content: '';
                    position: absolute;
                    inset: 0;
                    z-index: 0;
                    pointer-events: none;
                    opacity: 0.16;
                    background-image:
                        linear-gradient(rgba(201, 163, 58, 0.09) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(201, 163, 58, 0.09) 1px, transparent 1px);
                    background-size: 52px 52px;
                    mask-image: radial-gradient(circle at center, #000 0%, transparent 72%);
                }

                .free-sketch-lightbox-media--model model-viewer {
                    position: relative;
                    z-index: 2;
                    outline: none;
                    filter: saturate(1.03) contrast(1.02);
                    --poster-color: transparent;
                }

                .free-sketch-model-hint {
                    position: absolute;
                    top: 18px;
                    left: 18px;
                    z-index: 6;
                    display: inline-flex;
                    align-items: center;
                    gap: 9px;
                    max-width: calc(100% - 36px);
                    padding: 10px 14px;
                    border: 1px solid rgba(201, 163, 58, 0.34);
                    border-radius: 999px;
                    background: rgba(5, 5, 5, 0.68);
                    box-shadow: 0 10px 34px rgba(0, 0, 0, 0.34);
                    backdrop-filter: blur(14px);
                    color: rgba(242, 217, 132, 0.84);
                    font-family: Arial, sans-serif;
                    font-size: 10px;
                    font-weight: 700;
                    line-height: 1;
                    letter-spacing: 0.11em;
                    text-transform: uppercase;
                    pointer-events: none;
                    transition: opacity 0.35s ease, transform 0.35s ease;
                }

                .free-sketch-model-hint::before {
                    content: '';
                    width: 6px;
                    height: 6px;
                    flex: 0 0 6px;
                    border-radius: 50%;
                    background: #f2d984;
                    box-shadow: 0 0 14px rgba(242, 217, 132, 0.8);
                }

                .free-sketch-lightbox-media--interacted .free-sketch-model-hint {
                    opacity: 0;
                    transform: translateY(-6px);
                }

                .free-sketch-zoom-controls {
                    position: absolute;
                    left: 50%;
                    bottom: 18px;
                    z-index: 7;
                    display: inline-flex;
                    align-items: center;
                    gap: 3px;
                    padding: 5px;
                    transform: translateX(-50%);
                    border: 1px solid rgba(201, 163, 58, 0.4);
                    border-radius: 999px;
                    background: rgba(4, 4, 4, 0.76);
                    box-shadow:
                        0 16px 44px rgba(0, 0, 0, 0.5),
                        inset 0 1px 0 rgba(255, 255, 255, 0.04);
                    backdrop-filter: blur(16px);
                }

                .free-sketch-zoom-controls button {
                    appearance: none;
                    display: grid;
                    place-items: center;
                    width: 40px;
                    height: 40px;
                    padding: 0;
                    border: 0;
                    border-radius: 50%;
                    background: transparent;
                    color: #f2d984;
                    font-family: Arial, sans-serif;
                    font-size: 20px;
                    line-height: 1;
                    cursor: pointer;
                    transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
                }

                .free-sketch-zoom-controls button[aria-label="Сбросить масштаб"] {
                    width: 62px;
                    border-radius: 999px;
                    color: rgba(242, 217, 132, 0.78);
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 0.05em;
                }

                .free-sketch-zoom-controls button:hover {
                    background: #f2d984;
                    color: #111;
                    transform: translateY(-1px);
                }

                .free-sketch-zoom-controls button:focus-visible {
                    outline: 1px solid #f2d984;
                    outline-offset: 2px;
                }

                .free-sketch-lightbox-info {
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-end;
                    gap: 12px;
                    padding: 50px 0 0;
                }

                .free-sketch-lightbox-title {
                    color: #f2d984;
                    font-family: Georgia, "Times New Roman", serif;
                    font-size: 32px;
                    line-height: 1.1;
                }

                .free-sketch-lightbox-text {
                    color: rgba(232, 221, 198, 0.7);
                    font-family: Arial, sans-serif;
                    font-size: 15px;
                    line-height: 1.45;
                }

                .free-sketch-lightbox-cta {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 56px;
                    margin-top: 12px;
                    background: #c9a33a;
                    color: #111;
                    text-decoration: none;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    font-family: Arial, sans-serif;
                    font-size: 13px;
                    font-weight: 700;
                }

                .free-sketch-lightbox-cta:hover {
                    background: #f2d984;
                }

                @media (max-width: 900px) {
                    .free-sketch-lightbox {
                        padding: 14px;
                    }

                    .free-sketch-lightbox-panel {
                        grid-template-columns: 1fr;
                        gap: 14px;
                        padding: 14px;
                        overflow: auto;
                    }

                    .free-sketch-lightbox-media,
                    .free-sketch-lightbox-media model-viewer {
                        min-height: 58vh;
                        height: 58vh;
                    }

                    .free-sketch-lightbox-info {
                        padding: 0;
                    }

                    .free-sketch-lightbox-title {
                        font-size: 26px;
                    }

                    .free-sketch-model-hint {
                        top: 12px;
                        left: 12px;
                        max-width: calc(100% - 24px);
                        padding: 9px 11px;
                        font-size: 9px;
                        letter-spacing: 0.08em;
                    }

                    .free-sketch-zoom-controls {
                        bottom: 12px;
                    }
                }
            `;
            document.head.appendChild(lightboxStyle);
        }

        if (!document.getElementById('free-sketch-model-viewer-style-clean')) {
            const modelStyle = document.createElement('style');
            modelStyle.id = 'free-sketch-model-viewer-style-clean';
            modelStyle.textContent = `
                .free-sketch-preview {
                    position: relative;
                    overflow: hidden;
                }

                .free-sketch-preview--model {
                    min-height: 315px;
                    background-color: #050505;
                    background-position: center;
                    background-size: cover;
                    background-repeat: no-repeat;
                }

                .free-sketch-preview--model model-viewer {
                    display: block;
                    width: 100%;
                    height: 315px;
                    min-height: 315px;
                    background: transparent;
                    cursor: grab;
                    pointer-events: auto !important;
                    position: relative;
                    z-index: 2;
                    --poster-color: transparent;
                }

                .free-sketch-preview--model model-viewer:active {
                    cursor: grabbing;
                }

                @media (max-width: 640px) {
                    .free-sketch-preview--model,
                    .free-sketch-preview--model model-viewer {
                        min-height: 300px;
                        height: 300px;
                    }
                }
            `;
            document.head.appendChild(modelStyle);
        }
}

    function hideOldExamplesBlock() {
        if (!isFreeSketches) return;

        document.body.classList.add('category-free-sketches-page');

        const headings = Array.from(document.querySelectorAll('h1, h2, h3'));

        headings.forEach(function (heading) {
            const text = (heading.textContent || '').trim().toLowerCase();

            if (!text.includes('примеры работ')) return;

            let block = heading.closest('section');

            if (!block) {
                block = heading.parentElement;
            }

            if (block) {
                block.classList.add('old-examples-hidden');
            }
        });

        Array.from(document.querySelectorAll('div, section, article')).forEach(function (el) {
            const text = (el.textContent || '').trim().toLowerCase();
            const rect = el.getBoundingClientRect();

            if (
                text.includes('фото проекта') &&
                rect.width > 400 &&
                rect.height > 300
            ) {
                const block = el.closest('section') || el.parentElement;
                if (block) {
                    block.classList.add('old-examples-hidden');
                }
            }
        });
    }

    function createPreview(file, className) {
        const preview = document.createElement('div');
        preview.className = className;
        preview.setAttribute('role', 'button');
        preview.setAttribute('tabindex', '0');
        preview.setAttribute('aria-label', 'Открыть просмотр эскиза');

        if (file.media_type === 'image') {
            const img = document.createElement('img');
            img.src = file.file_path;
            img.alt = file.alt_text || file.title || '';
            preview.appendChild(img);
            return preview;
        }

        if (file.media_type === 'video') {
            preview.classList.add('free-sketch-preview--video');

            const video = document.createElement('video');
            video.muted = true;
            video.playsInline = true;
            video.preload = 'metadata';

            if (file.poster_path) video.poster = file.poster_path;

            const source = document.createElement('source');
            source.src = file.file_path;

            video.appendChild(source);
            preview.appendChild(video);

            const badge = document.createElement('div');
            badge.className = 'free-sketch-preview-badge';
            badge.textContent = 'Смотреть видео';
            preview.appendChild(badge);

            return preview;
        }

        if (file.media_type === 'model') {
            preview.classList.add(
                'free-sketch-preview--model-card',
                'ats-free-model-stage'
            );

            /*
             * Эта ветка универсальна:
             * любой будущий media_type === 'model'
             * получает тот же inline 3D viewer.
             */
            preview.setAttribute('role', 'group');
            preview.removeAttribute('tabindex');
            preview.setAttribute(
                'aria-label',
                file.alt_text ||
                    file.title ||
                    'Интерактивная 3D-модель'
            );

            const viewer =
                document.createElement('model-viewer');

            viewer.className =
                'ats-free-model-viewer';

            viewer.setAttribute(
                'src',
                cacheBustedMediaUrl(file)
            );

            viewer.setAttribute(
                'alt',
                file.alt_text ||
                    file.title ||
                    '3D-модель'
            );

            viewer.setAttribute(
                'camera-controls',
                ''
            );

            viewer.setAttribute(
                'auto-rotate',
                ''
            );

            viewer.setAttribute(
                'auto-rotate-delay',
                '0'
            );

            viewer.setAttribute(
                'rotation-per-second',
                '14deg'
            );

            viewer.setAttribute(
                'interaction-prompt',
                'auto'
            );

            viewer.setAttribute(
                'interaction-prompt-threshold',
                '1000'
            );

            viewer.setAttribute(
                'shadow-intensity',
                '0.5'
            );

            viewer.setAttribute(
                'exposure',
                '1'
            );

            viewer.setAttribute(
                'tone-mapping',
                'neutral'
            );

            viewer.setAttribute(
                'field-of-view',
                '36deg'
            );

            viewer.setAttribute(
                'min-field-of-view',
                '18deg'
            );

            viewer.setAttribute(
                'max-field-of-view',
                '78deg'
            );

            viewer.setAttribute(
                'disable-pan',
                ''
            );

            viewer.setAttribute(
                'loading',
                'lazy'
            );

            /*
             * До клика пользователь видит
             * обычный WebP-постер.
             */
            viewer.setAttribute(
                'reveal',
                'manual'
            );

            viewer.setAttribute(
                'touch-action',
                'pan-y'
            );

            if (file.poster_path) {
                viewer.setAttribute(
                    'poster',
                    file.poster_path
                );
            }

            preview.appendChild(viewer);

            if (file.poster_path) {
                const poster =
                    document.createElement('img');

                poster.className =
                    'ats-free-model-poster';

                poster.src =
                    file.poster_path;

                poster.alt =
                    file.alt_text ||
                    file.title ||
                    '3D-модель';

                poster.loading = 'lazy';
                poster.decoding = 'async';

                preview.appendChild(poster);
            }

            const button =
                document.createElement('button');

            button.type = 'button';
            button.className =
                'ats-free-model-open';
            button.textContent =
                'Посмотреть в 3D';

            preview.appendChild(button);

            const hint =
                document.createElement('div');

            hint.className =
                'ats-free-model-hint';
            hint.textContent =
                'Потяни модель, чтобы повернуть';

            preview.appendChild(hint);


            function revealModel() {
                preview.classList.add(
                    'is-3d-open'
                );

                // ATS_FREE_MODEL_AUTO_CENTER_V2
                const card = preview.closest(
                    '.free-sketch-card'
                );

                if (card) {
                    requestAnimationFrame(
                        function () {
                            card.scrollIntoView({
                                behavior: 'smooth',
                                block: 'center',
                                inline: 'center'
                            });
                        }
                    );
                }

                viewer.setAttribute(
                    'auto-rotate',
                    ''
                );

                viewer.setAttribute(
                    'auto-rotate-delay',
                    '0'
                );

                if (
                    typeof viewer.dismissPoster
                    === 'function'
                ) {
                    viewer.dismissPoster();
                } else {
                    viewer.removeAttribute(
                        'poster'
                    );
                }

                button.remove();
            }


            button.addEventListener(
                'click',
                function (event) {
                    event.preventDefault();
                    event.stopPropagation();

                    button.disabled = true;
                    button.textContent =
                        'Загрузка 3D…';

                    viewer.setAttribute(
                        'loading',
                        'eager'
                    );

                    if (viewer.loaded === true) {
                        revealModel();
                        return;
                    }

                    viewer.addEventListener(
                        'load',
                        revealModel,
                        { once: true }
                    );

                    viewer.addEventListener(
                        'error',
                        function () {
                            button.disabled = false;
                            button.textContent =
                                'Повторить 3D';
                        },
                        { once: true }
                    );
                }
            );


            [
                'pointerdown',
                'mousedown',
                'touchstart',
                'wheel',
                'click'
            ].forEach(function (eventName) {
                viewer.addEventListener(
                    eventName,
                    function (event) {
                        event.stopPropagation();
                    },
                    { passive: true }
                );
            });

            return preview;
        }

        preview.textContent = 'Медиа';
        return preview;
    }

    function closeFreeSketchLightbox() {
        const existing = document.querySelector('.free-sketch-lightbox');
        if (existing) existing.remove();
        document.body.classList.remove('free-sketch-lightbox-open');
    }


    function cacheBustedMediaUrl(file) {
        const base = file.file_path || '';
        const stamp = [
            file.id || '',
            file.file_size || '',
            file.updated_at || '',
            Date.now()
        ].filter(Boolean).join('-');

        return base + (base.includes('?') ? '&' : '?') + 'v=' + encodeURIComponent(stamp || Date.now());
    }

    function createLightboxMedia(file) {
        const mediaWrap = document.createElement('div');
        mediaWrap.className = 'free-sketch-lightbox-media';

        if (file.media_type === 'image') {
            mediaWrap.classList.add('free-sketch-lightbox-media--zoomable-image');

            const img = document.createElement('img');
            img.src = file.file_path;
            img.alt = file.alt_text || file.title || '';
            img.className = 'free-sketch-lightbox-zoom-target';
            mediaWrap.appendChild(img);
            return mediaWrap;
        }

        if (file.media_type === 'video') {
            const video = document.createElement('video');
            video.controls = true;
            video.playsInline = true;
            video.preload = 'metadata';

            if (file.poster_path) video.poster = file.poster_path;

            const source = document.createElement('source');
            source.src = file.file_path;

            video.appendChild(source);
            mediaWrap.appendChild(video);
            return mediaWrap;
        }

        if (file.media_type === 'model') {
            const viewer = document.createElement('model-viewer');

            viewer.setAttribute('src', cacheBustedMediaUrl(file));
            viewer.setAttribute('alt', file.alt_text || file.title || '3D-модель');
            viewer.setAttribute('camera-controls', '');
            viewer.setAttribute('max-camera-orbit', 'auto 165deg auto');
            viewer.setAttribute('min-camera-orbit', 'auto 15deg auto');
            viewer.setAttribute('camera-orbit', '0deg 75deg auto');
            viewer.setAttribute('interaction-prompt', 'none');
            viewer.setAttribute('disable-pan', '');
            viewer.setAttribute('touch-action', 'none');
            viewer.setAttribute('loading', 'eager');
            viewer.setAttribute('reveal', 'auto');
            viewer.setAttribute('shadow-intensity', '0.75');
            viewer.setAttribute('exposure', '1');
            viewer.setAttribute('field-of-view', '36deg');
            viewer.setAttribute('min-field-of-view', '15deg');
            viewer.setAttribute('max-field-of-view', '80deg');
            viewer.setAttribute('ar', '');
            viewer.setAttribute('tabindex', '0');

            if (file.poster_path) {
                viewer.setAttribute('poster', file.poster_path);
            }

            ['pointerdown', 'mousedown', 'touchstart', 'wheel'].forEach(function (eventName) {
                viewer.addEventListener(eventName, function (event) {
                    event.stopPropagation();
                    mediaWrap.classList.add('free-sketch-lightbox-media--interacted');
                }, { passive: true });
            });

            mediaWrap.classList.add('free-sketch-lightbox-media--model');
            mediaWrap.appendChild(viewer);

            const hint = document.createElement('div');
            hint.className = 'free-sketch-model-hint';
            hint.textContent = 'Вращение модели · масштаб кнопками или колесом';
            mediaWrap.appendChild(hint);
            return mediaWrap;
        }

        const link = document.createElement('a');
        link.href = file.file_path;
        link.target = '_blank';
        link.textContent = 'Открыть файл';
        mediaWrap.appendChild(link);

        return mediaWrap;
    }


    function installFreeSketchZoomControls(mediaWrap, file) {
        if (!file || !['image', 'model'].includes(file.media_type)) return;
        if (mediaWrap.querySelector('.free-sketch-zoom-controls')) return;

        const controls = document.createElement('div');
        controls.className = 'free-sketch-zoom-controls';

        const zoomOut = document.createElement('button');
        zoomOut.type = 'button';
        zoomOut.textContent = '−';
        zoomOut.setAttribute('aria-label', 'Отдалить');

        const reset = document.createElement('button');
        reset.type = 'button';
        reset.textContent = '100%';
        reset.setAttribute('aria-label', 'Сбросить масштаб');

        const zoomIn = document.createElement('button');
        zoomIn.type = 'button';
        zoomIn.textContent = '+';
        zoomIn.setAttribute('aria-label', 'Приблизить');

        controls.appendChild(zoomOut);
        controls.appendChild(reset);
        controls.appendChild(zoomIn);
        mediaWrap.appendChild(controls);

        if (file.media_type === 'image') {
            const target = mediaWrap.querySelector('.free-sketch-lightbox-zoom-target');
            if (!target) return;

            let scale = 1;
            let offsetX = 0;
            let offsetY = 0;
            let dragging = false;
            let startX = 0;
            let startY = 0;

            function applyImageZoom() {
                target.style.transform = 'translate(' + offsetX + 'px, ' + offsetY + 'px) scale(' + scale + ')';
                target.style.cursor = scale > 1 ? 'grab' : 'zoom-in';
                reset.textContent = Math.round(scale * 100) + '%';
            }

            function setImageZoom(nextScale) {
                const oldScale = scale;
                scale = Math.max(1, Math.min(4, nextScale));

                if (scale === 1) {
                    offsetX = 0;
                    offsetY = 0;
                } else if (oldScale === 1) {
                    offsetX = 0;
                    offsetY = 0;
                }

                applyImageZoom();
            }

            zoomIn.addEventListener('click', function (event) {
                event.stopPropagation();
                setImageZoom(scale + 0.25);
            });

            zoomOut.addEventListener('click', function (event) {
                event.stopPropagation();
                setImageZoom(scale - 0.25);
            });

            reset.addEventListener('click', function (event) {
                event.stopPropagation();
                scale = 1;
                offsetX = 0;
                offsetY = 0;
                applyImageZoom();
            });

            target.addEventListener('wheel', function (event) {
                event.preventDefault();
                event.stopPropagation();

                if (event.deltaY < 0) {
                    setImageZoom(scale + 0.15);
                } else {
                    setImageZoom(scale - 0.15);
                }
            }, { passive: false });

            target.addEventListener('pointerdown', function (event) {
                if (scale <= 1) return;

                dragging = true;
                startX = event.clientX - offsetX;
                startY = event.clientY - offsetY;
                target.setPointerCapture(event.pointerId);
                target.style.cursor = 'grabbing';
                event.stopPropagation();
            });

            target.addEventListener('pointermove', function (event) {
                if (!dragging) return;

                offsetX = event.clientX - startX;
                offsetY = event.clientY - startY;
                applyImageZoom();
                event.stopPropagation();
            });

            target.addEventListener('pointerup', function (event) {
                dragging = false;
                target.style.cursor = scale > 1 ? 'grab' : 'zoom-in';
                event.stopPropagation();
            });

            applyImageZoom();
            return;
        }

        if (file.media_type === 'model') {
            const viewer = mediaWrap.querySelector('model-viewer');
            if (!viewer) return;

            let fov = 36;

            function applyModelZoom() {
                fov = Math.max(15, Math.min(80, fov));
                viewer.setAttribute('field-of-view', fov + 'deg');
                reset.textContent = Math.round((36 / fov) * 100) + '%';
            }

            zoomIn.addEventListener('click', function (event) {
                event.stopPropagation();
                fov -= 5;
                applyModelZoom();
            });

            zoomOut.addEventListener('click', function (event) {
                event.stopPropagation();
                fov += 5;
                applyModelZoom();
            });

            reset.addEventListener('click', function (event) {
                event.stopPropagation();
                fov = 36;
                viewer.setAttribute('camera-orbit', '0deg 75deg auto');
                applyModelZoom();
            });

            viewer.addEventListener('wheel', function (event) {
                event.preventDefault();
                event.stopPropagation();

                if (event.deltaY < 0) {
                    fov -= 3;
                } else {
                    fov += 3;
                }

                applyModelZoom();
            }, { passive: false });

            applyModelZoom();
        }
    }

    function openFreeSketchLightbox(file) {
        closeFreeSketchLightbox();

        const overlay = document.createElement('div');
        overlay.className = 'free-sketch-lightbox';

        const panel = document.createElement('div');
        panel.className = 'free-sketch-lightbox-panel';

        const closeButton = document.createElement('button');
        closeButton.className = 'free-sketch-lightbox-close';
        closeButton.type = 'button';
        closeButton.setAttribute('aria-label', 'Закрыть');
        closeButton.textContent = '×';

        const media = createLightboxMedia(file);
        installFreeSketchZoomControls(media, file);

        const info = document.createElement('div');
        info.className = 'free-sketch-lightbox-info';

        const title = document.createElement('div');
        title.className = 'free-sketch-lightbox-title';
        title.textContent = file.title || file.original_filename || 'Свободный эскиз';

        const text = document.createElement('div');
        text.className = 'free-sketch-lightbox-text';
        text.textContent = file.alt_text || 'Свободный эскиз для татуировки';

        const cta = document.createElement('a');
        cta.className = 'free-sketch-lightbox-cta';
        cta.href = requestUrlForSketch(file);
        cta.textContent = 'Хочу этот эскиз';

        info.appendChild(title);
        info.appendChild(text);
        info.appendChild(cta);

        panel.appendChild(closeButton);
        panel.appendChild(media);
        panel.appendChild(info);
        overlay.appendChild(panel);
        document.body.appendChild(overlay);
        document.body.classList.add('free-sketch-lightbox-open');

        closeButton.addEventListener('click', closeFreeSketchLightbox);

        overlay.addEventListener('click', function (event) {
            if (event.target === overlay) {
                closeFreeSketchLightbox();
            }
        });

        document.addEventListener('keydown', function onKeydown(event) {
            if (event.key === 'Escape') {
                closeFreeSketchLightbox();
                document.removeEventListener('keydown', onKeydown);
            }
        });
    }

    function requestUrlForSketch(file) {
        const params = new URLSearchParams();

        params.set('source', 'free_sketch');
        params.set('service', 'free_sketch');
        params.set('category', 'free-sketches');

        if (file.id) {
            params.set('media_id', file.id);
        }

        if (file.title || file.original_filename) {
            params.set('sketch', file.title || file.original_filename);
        }

        return '/request?' + params.toString();
    }

    function findInsertPoint() {
        const main = document.querySelector('main') || document.body;

        const heroCandidates = Array.from(main.querySelectorAll('section, div'))
            .filter(function (el) {
                const text = (el.textContent || '').toLowerCase();
                const rect = el.getBoundingClientRect();

                return (
                    text.includes('свободные эскизы') &&
                    rect.width > 500 &&
                    rect.height > 120
                );
            });

        if (heroCandidates.length) {
            const hero = heroCandidates[0];
            return {
                parent: hero.parentElement || main,
                before: hero.nextSibling
            };
        }

        return {
            parent: main,
            before: main.firstChild
        };
    }

    function renderFreeSketchesCarousel(media) {
        installStyles();
        hideOldExamplesBlock();

        if (!media || !media.length) return;
        if (document.querySelector('.free-sketches-carousel-section')) return;

        const section = document.createElement('section');
        section.className = 'free-sketches-carousel-section';

        section.innerHTML = `
            <div class="free-sketches-carousel-head">
                <div>
                    <h2 class="free-sketches-carousel-title">Доступные эскизы</h2>
                    <div class="free-sketches-carousel-subtitle">
                        Готовые авторские эскизы, которые можно забрать в работу или адаптировать под тело.
                    </div>
                </div>

                <div class="free-sketches-carousel-controls">
                    <button class="free-sketches-carousel-button" type="button" data-direction="-1" aria-label="Назад">‹</button>
                    <button class="free-sketches-carousel-button" type="button" data-direction="1" aria-label="Вперёд">›</button>
                </div>
            </div>

            <div class="free-sketches-carousel-track"></div>
        `;

        const track = section.querySelector('.free-sketches-carousel-track');

        media.forEach(function (file, index) {
            const card = document.createElement('article');
            card.className = 'free-sketch-card';

            const preview = createPreview(file, 'free-sketch-preview');

            preview.addEventListener('click', function () {
                openFreeSketchLightbox(file);
            });

            preview.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    openFreeSketchLightbox(file);
                }
            });

            card.appendChild(preview);

            const name = document.createElement('div');
            name.className = 'free-sketch-name';
            name.textContent = file.title || file.original_filename || ('Эскиз #' + (index + 1));

            const meta = document.createElement('div');
            meta.className = 'free-sketch-meta';
            meta.textContent = file.alt_text || 'Свободный эскиз для татуировки';

            const cta = document.createElement('a');
            cta.className = 'free-sketch-cta';
            cta.href = requestUrlForSketch(file);
            cta.textContent = 'Хочу этот эскиз';

            card.appendChild(name);
            card.appendChild(meta);
            card.appendChild(cta);

            track.appendChild(card);
        });

        section.querySelectorAll('.free-sketches-carousel-button').forEach(function (button) {
            button.addEventListener('click', function () {
                const direction = Number(button.dataset.direction || 1);
                const amount = Math.min(track.clientWidth * 0.86, 380);

                track.scrollBy({
                    left: amount * direction,
                    behavior: 'smooth'
                });
            });
        });

        const insert = findInsertPoint();
        insert.parent.insertBefore(section, insert.before);
    }

    function renderDefaultMedia(media) {
        installStyles();

        if (!media || !media.length) return;
        if (document.querySelector('.category-media-section')) return;

        const section = document.createElement('section');
        section.className = 'category-media-section';

        const title = document.createElement('h2');
        title.className = 'category-media-title';
        title.textContent = 'Примеры работ';

        const grid = document.createElement('div');
        grid.className = 'category-media-grid';

        media.forEach(function (file) {
            const card = document.createElement('article');
            card.className = 'category-media-card';

            card.appendChild(createPreview(file, 'category-media-preview'));

            const name = document.createElement('div');
            name.className = 'category-media-name';
            name.textContent = file.title || file.original_filename || 'Медиа';

            card.appendChild(name);
            grid.appendChild(card);
        });

        section.appendChild(title);
        section.appendChild(grid);

        const main = document.querySelector('main') || document.body;
        main.appendChild(section);
    }

    fetch('/api/category-media/' + encodeURIComponent(slug))
        .then(function (response) {
            if (!response.ok) throw new Error('category media api error');
            return response.json();
        })
        .then(function (data) {
            if (isFreeSketches) {
                renderFreeSketchesCarousel(data.media || []);
            } else {
                renderDefaultMedia(data.media || []);
            }
        })
        .catch(function () {
            if (isFreeSketches) {
                hideOldExamplesBlock();
            }
        });
})();


/* ATS_3D_VIEW_UI_V1 */
(() => {
    const style = document.createElement("style");
    style.textContent = `
        @media (min-width: 901px) {
            .free-sketch-lightbox-panel {
                width: min(1380px, 97vw) !important;
                grid-template-columns: minmax(0, 1fr) clamp(220px, 17vw, 260px) !important;
                gap: 14px !important;
                padding: 16px !important;
            }

            .free-sketch-lightbox-info {
                justify-content: center !important;
                gap: 10px !important;
                padding: 52px 4px 22px !important;
            }

            .free-sketch-lightbox-title {
                font-size: clamp(24px, 2vw, 30px) !important;
                line-height: 1.08 !important;
            }

            .free-sketch-lightbox-cta {
                width: auto !important;
                min-width: 180px !important;
                max-width: 210px !important;
                min-height: 44px !important;
                margin-top: 8px !important;
                padding: 0 20px !important;
                font-size: 14px !important;
            }
        }
    `;
    document.head.appendChild(style);
})();

/* ATS_FREE_SKETCH_FOCUS_CAROUSEL_V5_START */
(function () {
    "use strict";

    const pathname = window.location.pathname
        .replace(/\/+$/, "");

    if (pathname !== "/categories/free-sketches") {
        return;
    }

    const STYLE_ID =
        "atsFreeSketchFocusCarouselV5Style";

    function installStyles() {
        if (document.getElementById(STYLE_ID)) {
            return;
        }

        const style = document.createElement("style");

        style.id = STYLE_ID;

        style.textContent = `
            html.ats-free-sketch-focus-v5 {
                overflow-x: hidden;
            }

            html.ats-free-sketch-focus-v5
            .free-sketches-carousel-section {
                box-sizing: border-box !important;

                width: 100vw !important;
                max-width: none !important;

                margin-left:
                    calc(50% - 50vw) !important;
                margin-right:
                    calc(50% - 50vw) !important;

                padding-left: 0 !important;
                padding-right: 0 !important;

                overflow: visible !important;
            }

            html.ats-free-sketch-focus-v5
            .free-sketches-carousel-head {
                box-sizing: border-box !important;

                width: min(
                    1180px,
                    calc(100% - 48px)
                ) !important;

                margin-left: auto !important;
                margin-right: auto !important;
                margin-bottom: 8px !important;
            }

            html.ats-free-sketch-focus-v5
            .free-sketches-carousel-track {
                box-sizing: border-box !important;

                display: flex !important;
                align-items: center !important;

                width: 100% !important;

                gap: clamp(
                    18px,
                    2.2vw,
                    34px
                ) !important;

                overflow-x: auto !important;
                overflow-y: visible !important;

                scroll-snap-type:
                    x mandatory !important;

                scroll-behavior:
                    smooth !important;

                overscroll-behavior-x:
                    contain !important;

                padding-top: 38px !important;
                padding-bottom: 46px !important;

                scrollbar-width: none !important;
            }

            html.ats-free-sketch-focus-v5
            .free-sketches-carousel-track::-webkit-scrollbar {
                display: none !important;
            }

            html.ats-free-sketch-focus-v5
            .free-sketch-card {
                box-sizing: border-box !important;

                flex:
                    0 0 clamp(
                        360px,
                        46vw,
                        620px
                    ) !important;

                width:
                    clamp(
                        360px,
                        46vw,
                        620px
                    ) !important;

                max-width: 620px !important;
                min-height: 0 !important;

                scroll-snap-align:
                    center !important;

                opacity: 0.28 !important;

                filter:
                    saturate(0.48)
                    brightness(0.56) !important;

                transform:
                    scale(0.84) !important;

                transform-origin:
                    center center !important;

                transition:
                    opacity 260ms ease,
                    filter 260ms ease,
                    transform 260ms ease,
                    border-color 260ms ease,
                    box-shadow 260ms ease !important;

                cursor: pointer;
            }

            html.ats-free-sketch-focus-v5
            .free-sketch-card.is-active {
                opacity: 1 !important;

                filter:
                    none !important;

                transform:
                    scale(1) !important;

                border-color:
                    rgba(
                        232,
                        201,
                        104,
                        0.84
                    ) !important;

                box-shadow:
                    0 28px 78px
                    rgba(0, 0, 0, 0.58),
                    0 0 34px
                    rgba(205, 166, 53, 0.10)
                    !important;

                cursor: default;
            }

            html.ats-free-sketch-focus-v5
            .free-sketch-preview {
                box-sizing: border-box !important;

                width: 100% !important;
                height:
                    clamp(
                        500px,
                        67vh,
                        720px
                    ) !important;

                min-height: 0 !important;

                display: flex !important;
                align-items: center !important;
                justify-content: center !important;

                overflow: hidden !important;

                background:
                    radial-gradient(
                        circle at center,
                        rgba(
                            205,
                            166,
                            53,
                            0.055
                        ),
                        transparent 58%
                    ),
                    #171717 !important;
            }

            html.ats-free-sketch-focus-v5
            .free-sketch-preview img,
            html.ats-free-sketch-focus-v5
            .free-sketch-preview video,
            html.ats-free-sketch-focus-v5
            .free-sketch-preview--model-card img,
            html.ats-free-sketch-focus-v5
            .free-sketch-preview--video video {
                width: 100% !important;
                height: 100% !important;

                max-width: 100% !important;
                max-height: 100% !important;

                object-fit:
                    contain !important;

                object-position:
                    center center !important;

                background:
                    #171717 !important;
            }

            html.ats-free-sketch-focus-v5
            .free-sketch-name {
                font-size:
                    clamp(
                        25px,
                        2.2vw,
                        34px
                    ) !important;

                margin-top: 18px !important;
            }

            html.ats-free-sketch-focus-v5
            .free-sketch-meta {
                font-size: 14px !important;
            }

            html.ats-free-sketch-focus-v5
            .free-sketch-cta {
                min-height: 58px !important;
                font-size: 13px !important;
            }

            html.ats-free-sketch-focus-v5
            .ats-free-sketch-hero-single {
                grid-template-columns:
                    minmax(0, 1fr) !important;
            }

            html.ats-free-sketch-focus-v5
            .ats-free-sketch-direction-hidden {
                display: none !important;
            }

            @media (max-width: 900px) {
                html.ats-free-sketch-focus-v5
                .free-sketches-carousel-head {
                    width:
                        calc(100% - 32px) !important;
                }

                html.ats-free-sketch-focus-v5
                .free-sketch-card {
                    flex:
                        0 0 min(
                            84vw,
                            560px
                        ) !important;

                    width:
                        min(
                            84vw,
                            560px
                        ) !important;

                    transform:
                        scale(0.91) !important;
                }

                html.ats-free-sketch-focus-v5
                .free-sketch-card.is-active {
                    transform:
                        scale(1) !important;
                }

                html.ats-free-sketch-focus-v5
                .free-sketch-preview {
                    height:
                        min(
                            67vh,
                            610px
                        ) !important;
                }
            }

            @media (max-width: 640px) {
                html.ats-free-sketch-focus-v5
                .free-sketches-carousel-track {
                    gap: 14px !important;

                    padding-top:
                        26px !important;

                    padding-bottom:
                        34px !important;
                }

                html.ats-free-sketch-focus-v5
                .free-sketch-card {
                    flex:
                        0 0 88vw !important;

                    width:
                        88vw !important;

                    transform:
                        scale(0.94) !important;
                }

                html.ats-free-sketch-focus-v5
                .free-sketch-preview {
                    height:
                        min(
                            62vh,
                            540px
                        ) !important;
                }

                html.ats-free-sketch-focus-v5
                .free-sketch-name {
                    font-size:
                        25px !important;
                }
            }
        `;

        document.head.appendChild(style);
    }

    function hideDirectionImage() {
        const elements = Array.from(
            document.querySelectorAll(
                "main div, main span, main p"
            )
        );

        const placeholder = elements.find(
            function (element) {
                const text = String(
                    element.textContent || ""
                )
                    .replace(/\s+/g, " ")
                    .trim()
                    .toLowerCase();

                return (
                    text ===
                    "изображение направления"
                );
            }
        );

        if (!placeholder) {
            return;
        }

        const mediaBlock =
            placeholder.closest(
                "figure"
            )
            || placeholder.closest(
                "[class*='hero'][class*='media']"
            )
            || placeholder.closest(
                "[class*='hero'][class*='image']"
            )
            || placeholder.parentElement;

        if (!mediaBlock) {
            return;
        }

        mediaBlock.classList.add(
            "ats-free-sketch-direction-hidden"
        );

        const heroLayout =
            mediaBlock.parentElement;

        if (heroLayout) {
            heroLayout.classList.add(
                "ats-free-sketch-hero-single"
            );
        }
    }

    function setupCarousel() {
        const section = document.querySelector(
            ".free-sketches-carousel-section"
        );

        if (!section) {
            return false;
        }

        const track = section.querySelector(
            ".free-sketches-carousel-track"
        );

        const cards = Array.from(
            section.querySelectorAll(
                ".free-sketch-card"
            )
        );

        if (!track || !cards.length) {
            return false;
        }

        if (
            section.dataset
                .atsFocusCarouselV5 === "1"
        ) {
            return true;
        }

        section.dataset
            .atsFocusCarouselV5 = "1";

        document.documentElement.classList.add(
            "ats-free-sketch-focus-v5"
        );

        installStyles();
        hideDirectionImage();

        let activeIndex = 0;
        let scrollTimer = null;

        function normalizeIndex(index) {
            return (
                (
                    index
                    % cards.length
                )
                + cards.length
            ) % cards.length;
        }

        function updateSideGutters() {
            const activeCard =
                cards[activeIndex]
                || cards[0];

            if (!activeCard) {
                return;
            }

            const gutter = Math.max(
                16,
                (
                    track.clientWidth
                    - activeCard.offsetWidth
                ) / 2
            );

            track.style.paddingLeft =
                gutter + "px";

            track.style.paddingRight =
                gutter + "px";
        }

        function nearestCardIndex() {
            const trackCenter =
                track.scrollLeft
                + track.clientWidth / 2;

            let nearestIndex = 0;
            let nearestDistance =
                Number.POSITIVE_INFINITY;

            cards.forEach(
                function (card, index) {
                    const cardCenter =
                        card.offsetLeft
                        + card.offsetWidth / 2;

                    const distance =
                        Math.abs(
                            cardCenter
                            - trackCenter
                        );

                    if (
                        distance
                        < nearestDistance
                    ) {
                        nearestDistance =
                            distance;

                        nearestIndex = index;
                    }
                }
            );

            return nearestIndex;
        }

        function setActiveClasses() {
            cards.forEach(
                function (card, index) {
                    const isActive =
                        index === activeIndex;

                    card.classList.toggle(
                        "is-active",
                        isActive
                    );

                    card.setAttribute(
                        "aria-current",
                        isActive
                            ? "true"
                            : "false"
                    );
                }
            );
        }

        function centerCard(
            requestedIndex,
            behavior
        ) {
            activeIndex =
                normalizeIndex(
                    requestedIndex
                );

            setActiveClasses();
            updateSideGutters();

            const card =
                cards[activeIndex];

            const targetLeft =
                card.offsetLeft
                - (
                    track.clientWidth
                    - card.offsetWidth
                ) / 2;

            track.scrollTo({
                left: Math.max(
                    0,
                    targetLeft
                ),
                behavior:
                    behavior || "smooth"
            });
        }

        const oldButtons = Array.from(
            section.querySelectorAll(
                ".free-sketches-carousel-button"
            )
        );

        oldButtons.forEach(
            function (oldButton) {
                const newButton =
                    oldButton.cloneNode(true);

                oldButton.replaceWith(
                    newButton
                );

                newButton.addEventListener(
                    "click",
                    function () {
                        const direction =
                            Number(
                                newButton.dataset
                                    .direction
                                || 1
                            );

                        centerCard(
                            activeIndex
                            + direction,
                            "smooth"
                        );
                    }
                );
            }
        );

        cards.forEach(
            function (card, index) {
                card.addEventListener(
                    "click",
                    function (event) {
                        if (
                            index
                            === activeIndex
                        ) {
                            return;
                        }

                        if (
                            event.target.closest(
                                ".free-sketch-cta"
                            )
                        ) {
                            return;
                        }

                        event.preventDefault();
                        event.stopPropagation();

                        centerCard(
                            index,
                            "smooth"
                        );
                    },
                    true
                );
            }
        );

        track.addEventListener(
            "scroll",
            function () {
                window.clearTimeout(
                    scrollTimer
                );

                scrollTimer =
                    window.setTimeout(
                        function () {
                            activeIndex =
                                nearestCardIndex();

                            setActiveClasses();
                        },
                        90
                    );
            },
            {
                passive: true
            }
        );

        window.addEventListener(
            "resize",
            function () {
                updateSideGutters();

                window.requestAnimationFrame(
                    function () {
                        centerCard(
                            activeIndex,
                            "auto"
                        );
                    }
                );
            }
        );

        window.requestAnimationFrame(
            function () {
                updateSideGutters();

                window.requestAnimationFrame(
                    function () {
                        centerCard(
                            0,
                            "auto"
                        );
                    }
                );
            }
        );

        return true;
    }

    installStyles();
    hideDirectionImage();

    if (setupCarousel()) {
        return;
    }

    const observer =
        new MutationObserver(
            function () {
                hideDirectionImage();

                if (setupCarousel()) {
                    observer.disconnect();
                }
            }
        );

    observer.observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );
})();
 /* ATS_FREE_SKETCH_FOCUS_CAROUSEL_V5_END */


// ATS_FREE_SKETCH_HEAD_CENTER_V1
(function () {
    const path = window.location.pathname;

    if (
        ![
            '/categories/free-sketches',
            '/categories/free-sketch',
            '/categories/free_sketch'
        ].includes(path)
    ) {
        return;
    }

    const style =
        document.createElement('style');

    style.id =
        'atsFreeSketchHeadCenterV1';

    style.textContent = `

        body.category-free-sketches-page
        .free-sketches-carousel-section {
            margin-top: -30px !important;
            padding-top: 0 !important;
        }

        body.category-free-sketches-page
        .free-sketches-carousel-head {
            position: relative !important;

            display: block !important;

            margin:
                0 auto 10px !important;

            padding:
                0 70px !important;

            text-align:
                center !important;
        }

        body.category-free-sketches-page
        .free-sketches-carousel-title {
            width: 100% !important;

            margin:
                0 auto !important;

            text-align:
                center !important;

            line-height:
                .95 !important;
        }

        body.category-free-sketches-page
        .free-sketches-carousel-subtitle {
            max-width:
                650px !important;

            margin:
                8px auto 0 !important;

            text-align:
                center !important;

            line-height:
                1.35 !important;
        }

        body.category-free-sketches-page
        .free-sketches-carousel-track {
            margin-top:
                0 !important;
        }

        @media (max-height: 820px)
               and (min-width: 721px) {

            body.category-free-sketches-page
            .free-sketches-carousel-section {
                margin-top:
                    -42px !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-head {
                margin-bottom:
                    6px !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-subtitle {
                margin-top:
                    5px !important;
            }
        }

        @media (max-width: 720px) {

            body.category-free-sketches-page
            .free-sketches-carousel-section {
                margin-top:
                    -12px !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-head {
                padding:
                    0 8px !important;
            }

            body.category-free-sketches-page
            .free-sketches-carousel-title,
            body.category-free-sketches-page
            .free-sketches-carousel-subtitle {
                text-align:
                    center !important;
            }
        }
    `;

    document.head.appendChild(style);
})();


// ATS_FREE_LOGO_CERTIFICATE_SIZE_V1
(function () {
    const style = document.createElement('style');

    style.id = 'atsFreeLogoCertificateSizeV1';

    style.textContent = `
        .ats-free-header-logo img {
            height: 72px !important;
            width: auto !important;
            max-width: 340px !important;
        }

        @media (max-width: 768px) {
            .ats-free-header-logo img {
                height: 52px !important;
                max-width: 230px !important;
            }
        }
    `;

    document.head.appendChild(style);
})();
