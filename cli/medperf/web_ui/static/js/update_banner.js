(function () {
    "use strict";

    var DISMISS_STORAGE_KEY = "medperf-update-banner-dismissed";

    function getUpdateInfo() {
        if (window.clientUpdate && typeof window.clientUpdate === "object") {
            return window.clientUpdate;
        }
        return null;
    }

    function readBannerData(banner) {
        return {
            updateAvailable: banner.getAttribute("data-update-available") === "true",
            latestVersion: banner.getAttribute("data-latest-version") || "",
            currentVersion: banner.getAttribute("data-current-version") || "",
            upgradeCommand: banner.getAttribute("data-upgrade-command") || "pip install -U medperf",
        };
    }

    function applyUpdateInfo(banner, info) {
        if (!info) return readBannerData(banner);

        var merged = {
            updateAvailable: Boolean(info.update_available),
            latestVersion: info.latest_version || "",
            currentVersion: info.current_version || "",
            upgradeCommand: info.upgrade_command || "pip install -U medperf",
        };

        banner.setAttribute("data-update-available", merged.updateAvailable ? "true" : "false");
        banner.setAttribute("data-latest-version", merged.latestVersion);
        banner.setAttribute("data-current-version", merged.currentVersion);
        banner.setAttribute("data-upgrade-command", merged.upgradeCommand);
        return merged;
    }

    function isDismissedForVersion(latestVersion) {
        try {
            return localStorage.getItem(DISMISS_STORAGE_KEY) === latestVersion;
        } catch (_) {
            return false;
        }
    }

    function dismissForVersion(latestVersion) {
        try {
            localStorage.setItem(DISMISS_STORAGE_KEY, latestVersion);
        } catch (_) {}
    }

    function setInstructionsExpanded(expanded) {
        var panel = document.getElementById("client-update-instructions");
        var button = document.getElementById("client-update-instructions-btn");
        var label = document.getElementById("client-update-instructions-label");
        var chevron = document.getElementById("client-update-instructions-chevron");
        if (!panel || !button) return;

        if (expanded) {
            panel.classList.remove("hidden");
            panel.setAttribute("aria-hidden", "false");
            button.setAttribute("aria-expanded", "true");
            if (label) label.textContent = "Hide update steps";
            if (chevron) chevron.classList.add("rotate-180");
        } else {
            panel.classList.add("hidden");
            panel.setAttribute("aria-hidden", "true");
            button.setAttribute("aria-expanded", "false");
            if (label) label.textContent = "Show update steps";
            if (chevron) chevron.classList.remove("rotate-180");
        }
    }

    function copyElementText(elementId, button) {
        var element = document.getElementById(elementId);
        if (!element) return;

        var text = element.textContent || "";
        function onCopied() {
            if (!button) return;
            var original = button.textContent;
            button.textContent = "Copied";
            window.setTimeout(function () {
                button.textContent = original;
            }, 1500);
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(onCopied).catch(function () {});
            return;
        }

        var textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "absolute";
        textarea.style.left = "-9999px";
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand("copy");
            onCopied();
        } catch (_) {}
        document.body.removeChild(textarea);
    }

    function populateBannerContent(data) {
        var summary = document.getElementById("client-update-summary");
        var upgradeCommand = document.getElementById("client-update-upgrade-command");
        if (summary) {
            summary.innerHTML =
                "A new MedPerf release is available: " +
                "<strong class=\"font-semibold text-amber-800 dark:text-amber-200\">" + data.latestVersion + "</strong> " +
                "<span class=\"text-gray-600 dark:text-gray-300\">(you have " + data.currentVersion + ")</span>";
        }
        if (upgradeCommand) {
            upgradeCommand.textContent = data.upgradeCommand;
        }
    }

    function refreshClientUpdateBanner(overrideInfo) {
        var banner = document.getElementById("client-update-banner");
        if (!banner) return;

        var data = applyUpdateInfo(banner, overrideInfo || getUpdateInfo());
        setInstructionsExpanded(false);

        if (!data.updateAvailable || !data.latestVersion || isDismissedForVersion(data.latestVersion)) {
            banner.classList.add("hidden");
            return;
        }

        populateBannerContent(data);
        banner.classList.remove("hidden");
    }

    function bindUpdateBannerEvents() {
        var banner = document.getElementById("client-update-banner");
        if (!banner || banner.dataset.bound === "true") return;
        banner.dataset.bound = "true";

        var instructionsBtn = document.getElementById("client-update-instructions-btn");
        if (instructionsBtn) {
            instructionsBtn.addEventListener("click", function () {
                var panel = document.getElementById("client-update-instructions");
                var expanded = panel && !panel.classList.contains("hidden");
                setInstructionsExpanded(!expanded);
            });
        }

        var dismissBtn = document.getElementById("client-update-dismiss-btn");
        if (dismissBtn) {
            dismissBtn.addEventListener("click", function () {
                var latestVersion = banner.getAttribute("data-latest-version");
                if (latestVersion) dismissForVersion(latestVersion);
                banner.classList.add("hidden");
                setInstructionsExpanded(false);
            });
        }

        banner.querySelectorAll(".client-update-copy-btn").forEach(function (button) {
            button.addEventListener("click", function () {
                var targetId = button.getAttribute("data-copy-target");
                if (targetId) copyElementText(targetId, button);
            });
        });
    }

    function initializeUpdateBanner() {
        bindUpdateBannerEvents();
        refreshClientUpdateBanner();
    }

    window.refreshClientUpdateBanner = refreshClientUpdateBanner;

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeUpdateBanner);
    } else {
        initializeUpdateBanner();
    }
})();
