// === persistent side rails ===
    document.addEventListener('DOMContentLoaded', function () {
        const carousel = document.querySelector('.home-card-carousel');
        if (!carousel) return;

        const cards = Array.from(carousel.querySelectorAll('.main-card'));
        if (!cards.length) return;

        let ticking = false;

        function updatePersistentRails() {
            const center = carousel.scrollLeft + carousel.clientWidth / 2;

            let closestCard = null;
            let closestDistance = Infinity;

            cards.forEach(function (card) {
                const cardCenter = card.offsetLeft + card.offsetWidth / 2;
                const distance = Math.abs(center - cardCenter);

                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestCard = card;
                }
            });

            cards.forEach(function (card) {
                card.classList.remove('rail-left', 'rail-right', 'rail-active');

                const cardCenter = card.offsetLeft + card.offsetWidth / 2;

                if (card === closestCard) {
                    card.classList.add('rail-active');
                    return;
                }

                if (cardCenter < center) {
                    card.classList.add('rail-left');
                } else {
                    card.classList.add('rail-right');
                }
            });
        }

        function requestUpdate() {
            if (ticking) return;

            ticking = true;

            window.requestAnimationFrame(function () {
                updatePersistentRails();
                ticking = false;
            });
        }

        updatePersistentRails();

        setTimeout(updatePersistentRails, 100);
        setTimeout(updatePersistentRails, 350);
        setTimeout(updatePersistentRails, 800);

        carousel.addEventListener('scroll', requestUpdate, { passive: true });
        window.addEventListener('resize', requestUpdate);

        carousel.addEventListener('mouseup', function () {
            setTimeout(updatePersistentRails, 80);
            setTimeout(updatePersistentRails, 240);
        });

        carousel.addEventListener('touchend', function () {
            setTimeout(updatePersistentRails, 80);
            setTimeout(updatePersistentRails, 240);
        });

        carousel.addEventListener('click', function () {
            setTimeout(updatePersistentRails, 120);
            setTimeout(updatePersistentRails, 360);
        });
    });
    // === /persistent side rails ===
