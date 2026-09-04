(() => {
    const initFreeSketchAutoRotate = () => {
        document
            .querySelectorAll(".japanese-free-sketch-model")
            .forEach((viewer) => {
                const shell = viewer.closest(
                    ".japanese-free-sketch-card__viewer"
                );

                if (!shell) {
                    return;
                }

                const revealLiveModel = () => {
                    shell.classList.add("is-3d-open");

                    if (
                        typeof viewer.dismissPoster === "function"
                    ) {
                        viewer.dismissPoster();
                    }
                };

                if (viewer.loaded) {
                    revealLiveModel();
                } else {
                    viewer.addEventListener(
                        "load",
                        revealLiveModel,
                        { once: true }
                    );
                }
            });
    };

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initFreeSketchAutoRotate,
            { once: true }
        );
    } else {
        initFreeSketchAutoRotate();
    }
})();
