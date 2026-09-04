// === ArtToSlipAway skateboard deck holes ===
        document.addEventListener('DOMContentLoaded', function () {
            document.querySelectorAll('.home-card-carousel .main-card').forEach(function (card) {
                if (card.querySelector('.deck-holes')) {
                    return;
                }

                const topHoles = document.createElement('span');
                topHoles.className = 'deck-holes top';

                const bottomHoles = document.createElement('span');
                bottomHoles.className = 'deck-holes bottom';

                card.appendChild(topHoles);
                card.appendChild(bottomHoles);
            });
        });
