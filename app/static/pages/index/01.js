(function () {
            const track = document.getElementById("restored-home-card-carousel");
            if (!track) return;

            const cards = Array.from(track.querySelectorAll("[data-board-card]"));
            const prev = document.querySelector("[data-restored-carousel-prev]");
            const next = document.querySelector("[data-restored-carousel-next]");

            function updateActive() {
                if (!cards.length) return;

                const center = track.scrollLeft + track.clientWidth / 2;
                let active = cards[0];
                let best = Infinity;

                cards.forEach(function(card) {
                    const cardCenter = card.offsetLeft + card.offsetWidth / 2;
                    const distance = Math.abs(center - cardCenter);

                    if (distance < best) {
                        best = distance;
                        active = card;
                    }
                });

                cards.forEach(function(card) {
                    card.classList.toggle("is-active", card === active);
                    card.classList.remove("is-left", "is-right", "is-near");

                    if (card !== active) {
                        if (card.offsetLeft < active.offsetLeft) {
                            card.classList.add("is-left");
                        } else {
                            card.classList.add("is-right");
                        }
                    }
                });
            }

            function scrollByCard(direction) {
                const card = cards[0];
                const amount = card ? card.offsetWidth + 24 : 354;
                track.scrollBy({ left: amount * direction, behavior: "smooth" });
            }

            track.addEventListener("scroll", function () {
                window.requestAnimationFrame(updateActive);
            });

            if (prev) prev.addEventListener("click", function () { scrollByCard(-1); });
            if (next) next.addEventListener("click", function () { scrollByCard(1); });

            updateActive();
        })();
