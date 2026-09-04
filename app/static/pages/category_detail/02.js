(() => {
                    const viewer =
                        document.getElementById(
                            "certificate-model-viewer"
                        );

                    if (!viewer) {
                        return;
                    }

                    const shell =
                        viewer.closest(
                            ".certificate-model-shell"
                        );

                    if (!shell) {
                        return;
                    }

                    let stopTimer = null;

                    const stopAutoRotate = () => {
                        viewer.removeAttribute(
                            "auto-rotate"
                        );

                        if (stopTimer) {
                            clearTimeout(stopTimer);
                            stopTimer = null;
                        }
                    };

                    const reveal = () => {
                        shell.classList.add(
                            "is-loaded"
                        );

                        stopTimer =
                            setTimeout(
                                stopAutoRotate,
                                2400
                            );
                    };

                    if (viewer.loaded) {
                        reveal();
                    } else {
                        viewer.addEventListener(
                            "load",
                            reveal,
                            { once: true }
                        );
                    }

                    viewer.addEventListener(
                        "pointerdown",
                        stopAutoRotate,
                        { passive: true }
                    );

                    viewer.addEventListener(
                        "touchstart",
                        stopAutoRotate,
                        { passive: true }
                    );

                    viewer.addEventListener(
                        "wheel",
                        stopAutoRotate,
                        { passive: true }
                    );
                })();
