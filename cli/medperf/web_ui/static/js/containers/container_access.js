function getEmailsList(element) {
    var emailsArr = [];
    if (!element) return emailsArr;
    element.querySelectorAll(".email-chip").forEach(function (chip) {
        emailsArr.push((chip.textContent || "").replace(/\s*×\s*$/, "").trim());
    });
    return emailsArr;
}

function createEmailChip(email, inputElement) {
    var chip = document.createElement("div");
    chip.className = "email-chip inline-block bg-muted-strong rounded-full py-1 px-3 mr-2 mb-2 text-sm";
    chip.textContent = email;
    var remove = document.createElement("span");
    remove.className = "remove-btn ml-2 cursor-pointer font-bold";
    remove.textContent = "×";
    remove.addEventListener("click", function () { chip.remove(); });
    chip.appendChild(remove);
    if (inputElement && inputElement.parentNode) inputElement.parentNode.insertBefore(chip, inputElement);
}

function clearEmailChips(container) {
    if (!container) return;
    container.querySelectorAll(".email-chip").forEach(function (chip) { chip.remove(); });
}

function setEmailChips(container, emails) {
    clearEmailChips(container);
    var inputEl = container ? container.querySelector("input") : null;
    (emails || []).forEach(function (email) {
        email = (email || "").trim();
        if (email) createEmailChip(email, inputEl);
    });
}

function parseEmails(element) {
    if (!element || !element.getAttribute) return;
    var raw = element.getAttribute("data-allowed-list") || "[]";
    try {
        var jsonList = JSON.parse(raw);
        setEmailChips(element, jsonList);
    } catch (_) {}
}

function parseRunningAutoAccess(panel) {
    if (!panel) return {};
    try {
        return JSON.parse(panel.getAttribute("data-running-auto-access") || "{}");
    } catch (_) {
        return {};
    }
}

function getSelectedBenchmarkId() {
    var benchmarkEl = document.getElementById("benchmark-auto");
    return benchmarkEl && benchmarkEl.value ? benchmarkEl.value : "";
}

function getRunningStateForBenchmark(runningAutoAccess, benchmarkId) {
    if (!benchmarkId) return null;
    return runningAutoAccess[benchmarkId] || null;
}

function parseStoredEmails(emails) {
    if (!emails) return [];
    return String(emails).trim().split(/\s+/).filter(Boolean);
}

function setElementVisible(element, visible) {
    if (!element) return;
    element.style.display = visible ? "" : "none";
    element.classList.toggle("hidden", !visible);
}

function updateAutoAccessUI() {
    var panel = document.getElementById("auto-access-panel");
    var actionsEl = document.getElementById("auto-access-actions");
    var startBtn = document.getElementById("start-auto-access-btn");
    var stopBtn = document.getElementById("stop-auto-access-btn");
    var runningBadge = document.getElementById("running-badge");
    var benchmarkEl = document.getElementById("benchmark-auto");
    var intervalEl = document.getElementById("interval-auto");
    var emailContainer = document.getElementById("allowed-email-list-auto");
    var emailInput = document.getElementById("email-input-auto");
    var benchmarkId = getSelectedBenchmarkId();
    var runningAutoAccess = parseRunningAutoAccess(panel);
    var runningState = getRunningStateForBenchmark(runningAutoAccess, benchmarkId);
    var isRunning = Boolean(runningState);

    setElementVisible(startBtn, false);
    setElementVisible(stopBtn, false);
    setElementVisible(runningBadge, false);

    if (!benchmarkId) {
        setElementVisible(actionsEl, false);
        if (intervalEl) {
            intervalEl.value = "5";
            intervalEl.disabled = true;
        }
        if (emailInput) emailInput.disabled = true;
        if (benchmarkEl) benchmarkEl.disabled = false;
        clearEmailChips(emailContainer);
        return;
    }

    setElementVisible(actionsEl, true);

    if (isRunning) {
        if (intervalEl) {
            intervalEl.value = runningState.interval || 5;
            intervalEl.disabled = true;
        }
        if (emailInput) emailInput.disabled = true;
        if (benchmarkEl) benchmarkEl.disabled = true;
        setEmailChips(emailContainer, parseStoredEmails(runningState.emails));
        setElementVisible(stopBtn, true);
        setElementVisible(runningBadge, true);
    } else {
        if (intervalEl) {
            intervalEl.value = "5";
            intervalEl.disabled = false;
        }
        if (emailInput) emailInput.disabled = false;
        if (benchmarkEl) benchmarkEl.disabled = false;
        clearEmailChips(emailContainer);
        setElementVisible(startBtn, true);
    }
}

function checkAccessForm() {
    var allowListArr = getEmailsList(document.getElementById("allowed-email-list"));
    if (!document.getElementById("benchmark") || !document.getElementById("benchmark").value) {
        showErrorToast("Make sure that you've selected a benchmark");
        return false;
    }
    if (!allowListArr.length) {
        showErrorToast("Make sure that the email allow list is not empty");
        return false;
    }
    return true;
}

function checkAutoAccessForm() {
    var allowListArr = getEmailsList(document.getElementById("allowed-email-list-auto"));
    if (!getSelectedBenchmarkId()) {
        showErrorToast("Make sure that you've selected a benchmark");
        return false;
    }
    var intervalEl = document.getElementById("interval-auto");
    var interval = intervalEl ? Number(intervalEl.value) : 0;
    if (!interval || interval < 5 || interval > 60) {
        showErrorToast("Make sure that the time interval is between 5 and 60 (inclusive)");
        return false;
    }
    if (!allowListArr.length) {
        showErrorToast("Make sure that the email allow list is not empty");
        return false;
    }
    return true;
}

function startAutoGrant(startBtn) {
    disableElements(".card button, .card input, .card select");
    var panel = document.getElementById("auto-access-panel");
    var allowListArr = getEmailsList(document.getElementById("allowed-email-list-auto"));
    var formData = new FormData();
    formData.append("benchmark_id", getSelectedBenchmarkId());
    formData.append("model_id", panel ? panel.getAttribute("data-model-id") : "");
    formData.append("interval", document.getElementById("interval-auto").value);
    formData.append("emails", allowListArr.join(" "));
    ajaxRequest("/containers/start_auto_access", "POST", formData, function (response) {
        if (response && response.status === "success") showReloadModal({ title: "Successfully Started Auto Grant Access", seconds: 2 });
        else showErrorModal("Failed to Start Auto Grant Access", response);
    }, "Failed to start auto grant access");
}

function stopAutoGrant(stopBtn) {
    disableElements(".card button, .card input, .card select");
    var panel = document.getElementById("auto-access-panel");
    var formData = new FormData();
    formData.append("model_id", panel ? panel.getAttribute("data-model-id") : "");
    formData.append("benchmark_id", getSelectedBenchmarkId());
    ajaxRequest("/containers/stop_auto_access", "POST", formData, function (response) {
        if (response && response.status === "success") showReloadModal({ title: "Successfully Stopped Auto Grant Access", seconds: 2 });
        else showErrorModal("Failed to Stop Auto Grant Access", response);
    }, "Failed to stop auto grant access");
}

function showErrorToast(message) {
    showToast("Validation Error", message, "text-bg-danger");
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function init() {
    parseEmails(document.getElementById("allowed-email-list"));
    document.querySelectorAll(".email-input").forEach(function (input) {
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === " " || e.key === ",") {
                e.preventDefault();
                var email = this.value.trim().replace(/,$/, "");
                if (email && isValidEmail(email)) { createEmailChip(email, this); this.value = ""; }
            }
        });
        input.addEventListener("paste", function (e) {
            e.preventDefault();
            var clipboardData = (e.clipboardData || window.clipboardData).getData("text");
            clipboardData.split(/[\s,]+/).forEach(function (email) {
                email = email.trim();
                if (email && isValidEmail(email)) createEmailChip(email, input);
            });
            input.value = "";
        });
    });
    document.querySelectorAll("form[id$='-form']").forEach(function (form) {
        form.addEventListener("submit", function (e) {
            if (form.id === "grant-access-form") {
                e.preventDefault();
                if (!checkAccessForm()) return;
                var benchEl = document.getElementById("benchmark");
                var emailsEl = document.getElementById("form-emails");
                if (benchEl) document.getElementById("form-benchmark-id").value = benchEl.value;
                if (emailsEl) emailsEl.value = getEmailsList(document.getElementById("allowed-email-list")).join(" ");
                showConfirmModal(form, submitActionFormWithForm, form.getAttribute("data-confirm-message") || "continue?");
            } else {
                submitActionForm(e);
            }
        });
    });

    var benchmarkAutoEl = document.getElementById("benchmark-auto");
    if (benchmarkAutoEl) benchmarkAutoEl.addEventListener("change", updateAutoAccessUI);

    var startBtn = document.getElementById("start-auto-access-btn");
    if (startBtn) startBtn.addEventListener("click", function (e) {
        if (checkAutoAccessForm()) showConfirmModal(e.currentTarget, startAutoGrant, "start automatic grant access for the selected benchmark?");
    });
    var stopBtn = document.getElementById("stop-auto-access-btn");
    if (stopBtn) stopBtn.addEventListener("click", function (e) {
        showConfirmModal(e.currentTarget, stopAutoGrant, "stop automatic grant access?");
    });

    updateAutoAccessUI();
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();
