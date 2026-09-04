// === ArtToSlipAway deck cleanup ===
        document.addEventListener('DOMContentLoaded', function () {
            document.querySelectorAll('.home-card-carousel .main-card').forEach(function (card) {
                card.querySelectorAll(
                    '[class*="corner"], [class*="Corner"], .card-corner, .frame-corner, .corner-accent, .corner-piece, .deck-aura, .deck-cast-shadow, .deck-shell, .deck-face, .deck-grip, .deck-glow, .deck-holes, .deck-wheel, .deck-truck, .deck-side, .deck-top, .deck-edge-light, .deck-shade, .deck-shadow'
                ).forEach(function (el) {
                    el.remove();
                });

                const aura = document.createElement('span');
                aura.className = 'deck-aura';

                const shadow = document.createElement('span');
                shadow.className = 'deck-cast-shadow';

                const shell = document.createElement('span');
                shell.className = 'deck-shell';

                const face = document.createElement('span');
                face.className = 'deck-face';

                const grip = document.createElement('span');
                grip.className = 'deck-grip';

                const glow = document.createElement('span');
                glow.className = 'deck-glow';

                const holesTop = document.createElement('span');
                holesTop.className = 'deck-holes top';

                const holesBottom = document.createElement('span');
                holesBottom.className = 'deck-holes bottom';

                card.prepend(holesBottom);
                card.prepend(holesTop);
                card.prepend(glow);
                card.prepend(grip);
                card.prepend(face);
                card.prepend(shell);
                card.prepend(shadow);
                card.prepend(aura);
            });
        });
        // === /ArtToSlipAway deck cleanup ===
