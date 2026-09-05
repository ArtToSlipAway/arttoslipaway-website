(function () {
    let requestViewSent = false;
    let leadSentThisPage = false;

    function canTrack() {
        return typeof window.gtag === "function";
    }

    function paramsFromUrl(url) {
        const keys = [
            "source",
            "service",
            "category",
            "project",
            "sketch_id"
        ];
        const result = {};

        keys.forEach(function (key) {
            const value = url.searchParams.get(key);
            if (value) result[key] = value;
        });

        return result;
    }

    function trackRequestView() {
        if (!canTrack() || requestViewSent) return;
        if (location.pathname !== "/request") return;

        requestViewSent = true;
        const url = new URL(location.href);
        const data = paramsFromUrl(url);

        try {
            sessionStorage.setItem(
                "ats_request_context",
                JSON.stringify(data)
            );
        } catch (_) {}

        window.gtag("event", "request_view", data);
    }

    function trackLead() {
        if (!canTrack() || leadSentThisPage) return;
        if (location.pathname !== "/thanks") return;

        const url = new URL(location.href);
        const leadId = url.searchParams.get("lead_id");
        if (!leadId) return;

        const storageKey = "ats_ga_lead_" + leadId;

        try {
            if (localStorage.getItem(storageKey) === "1") return;
        } catch (_) {}

        let data = {};
        try {
            data = Object.assign(
                data,
                JSON.parse(
                    sessionStorage.getItem("ats_request_context") || "{}"
                )
            );
        } catch (_) {}

        window.gtag("event", "generate_lead", data);

        try {
            localStorage.setItem(storageKey, "1");
        } catch (_) {}

        leadSentThisPage = true;
    }

    function trackPage() {
        trackRequestView();
        trackLead();
    }

    document.addEventListener("click", function (event) {
        const accept = event.target.closest("#ats-cookie-accept");
        if (accept) {
            window.setTimeout(trackPage, 0);
            return;
        }

        const link = event.target.closest("a[href]");
        if (!link || !canTrack()) return;

        let url;
        try {
            url = new URL(link.href, location.href);
        } catch (_) {
            return;
        }

        if (
            url.origin !== location.origin
            || url.pathname !== "/request"
        ) {
            return;
        }

        const data = paramsFromUrl(url);
        data.page_path = location.pathname;
        data.link_text = (link.textContent || "").trim().slice(0, 80);
        window.gtag("event", "cta_click", data);
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", trackPage);
    } else {
        trackPage();
    }
})();
