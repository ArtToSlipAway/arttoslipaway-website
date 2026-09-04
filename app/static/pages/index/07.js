(function () {
    function removeLogoBoardOnly() {
        var tracks = document.querySelectorAll(".home-card-carousel");

        tracks.forEach(function(track) {
            var cards = Array.prototype.slice.call(track.querySelectorAll(".main-card"));

            cards.forEach(function(card) {
                var txt = (card.textContent || "").toLowerCase();

                if (txt.indexOf("логотип") !== -1 || txt.indexOf("logo") !== -1) {
                    card.parentNode && card.parentNode.removeChild(card);
                }
            });

            var alive = Array.prototype.slice.call(track.querySelectorAll(".main-card"));

            alive.forEach(function(card) {
                card.classList.remove("is-active");
                card.classList.remove("is-left");
                card.classList.remove("is-right");
                card.classList.remove("is-near");
            });

            if (!alive.length) return;

            var centerIndex = Math.min(1, alive.length - 1);

            alive.forEach(function(card, index) {
                if (index === centerIndex) {
                    card.classList.add("is-active");
                } else if (index < centerIndex) {
                    card.classList.add("is-left");
                } else {
                    card.classList.add("is-right");
                }
            });

            var active = alive[centerIndex];

            if (active && track.scrollTo) {
                var left = active.offsetLeft - ((track.clientWidth - active.offsetWidth) / 2);
                track.scrollTo({ left: left, behavior: "auto" });
            }
        });
    }

    function scheduleRemoveLogoBoardOnly() {
        removeLogoBoardOnly();
        setTimeout(removeLogoBoardOnly, 100);
        setTimeout(removeLogoBoardOnly, 350);
        setTimeout(removeLogoBoardOnly, 800);
        setTimeout(removeLogoBoardOnly, 1600);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", scheduleRemoveLogoBoardOnly);
    } else {
        scheduleRemoveLogoBoardOnly();
    }

    window.addEventListener("load", scheduleRemoveLogoBoardOnly);
})();
