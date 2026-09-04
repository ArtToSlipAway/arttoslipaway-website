(() => {
                    const viewer = document.getElementById(
                        "certificate-model-viewer"
                    );

                    if (!viewer) {
                        return;
                    }

                    const normalizeMaterials = () => {
                        const materials =
                            viewer.model?.materials || [];

                        for (const material of materials) {
                            const pbr =
                                material.pbrMetallicRoughness;

                            if (!pbr) {
                                continue;
                            }

                            /*
                             * Nomad записал материал как полностью
                             * металлический. На тёмной публичной
                             * странице он отражал белое окружение
                             * вместо нормального показа текстуры.
                             */
                            if (
                                typeof pbr.setMetallicFactor
                                === "function"
                            ) {
                                pbr.setMetallicFactor(0);
                            }

                            if (
                                typeof pbr.setRoughnessFactor
                                === "function"
                            ) {
                                pbr.setRoughnessFactor(0.68);
                            }
                        }
                    };

                    viewer.addEventListener(
                        "load",
                        () => {
                            /*
                             * ATS_CERTIFICATE_STABLE_LOAD_V1
                             *
                             * Сначала окончательно готовим материал,
                             * затем ждём два кадра и только после этого
                             * начинаем визуальное появление.
                             */
                            viewer.removeAttribute("auto-rotate");

                            normalizeMaterials();

                            requestAnimationFrame(() => {
                                normalizeMaterials();

                                requestAnimationFrame(() => {
                                    viewer.classList.add(
                                        "certificate-model-is-loaded"
                                    );
                                });
                            });
                        }
                    );
                })();
