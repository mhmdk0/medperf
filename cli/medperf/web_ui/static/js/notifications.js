/**
 * Notifications and toasts.
 *
 * Notifications are sent by the server when a task finishes (see the
 * "notification" events of /events/global in base.html). They are listed in
 * the navbar dropdown (#notifications-list), where they can be marked as read
 * or deleted, and new ones also pop up as a toast.
 *
 * Depends on common.js (escapeHtml, timeAgo), loaded right after this file.
 */

/** Toast colors per type. */
var TOAST_STYLES = {
    success: { bg: "bg-brand", fg: "text-ink" },
    danger: { bg: "bg-danger", fg: "text-white" },
    info: { bg: "bg-info", fg: "text-white" },
};
var TOAST_DURATION_MS = 5000;

/** Card colors of a notification in the list, per notification type. */
var NOTIFICATION_STYLES = {
    success: "bg-success-muted text-success border-success",
    info: "bg-info-muted text-info-fg border-info",
    failed: "bg-danger-muted text-danger-fg border-danger",
};

/**
 * Show a toast that disappears after a few seconds (or when closed).
 *
 * @param {string} title - bold first line.
 * @param {string} message - text below the title.
 * @param {string} [type="info"] - "success", "danger" or "info".
 */
function showToast(title, message, type) {
    var container = document.getElementById("toast-container");
    if (!container) return;
    var style = TOAST_STYLES[type] || TOAST_STYLES.info;

    var toastEl = document.createElement("div");
    toastEl.className = "toast-item pointer-events-auto flex items-center gap-3 " + style.bg + " " + style.fg + " rounded-xl shadow-lg px-4 py-3 border-0";
    toastEl.setAttribute("role", "alert");
    toastEl.setAttribute("aria-live", "assertive");
    toastEl.setAttribute("aria-atomic", "true");
    toastEl.innerHTML =
        "<div class=\"flex-1 min-w-0\">" +
        "<strong class=\"block\">" + escapeHtml(title) + "</strong>" +
        "<span class=\"text-sm opacity-90\">" + escapeHtml(message) + "</span>" +
        "</div>" +
        "<button type=\"button\" class=\"toast-close flex-shrink-0 w-8 h-8 rounded-lg hover:bg-white/20 flex items-center justify-center text-lg leading-none cursor-pointer\" aria-label=\"Close\">&times;</button>";
    container.appendChild(toastEl);

    toastEl.querySelector(".toast-close").addEventListener("click", function () { toastEl.remove(); });
    setTimeout(function () { toastEl.remove(); }, TOAST_DURATION_MS);
}

/**
 * Increment or decrement the unread notifications badge of the navbar bell.
 */
function changeNotificationCount(increment) {
    var el = document.getElementById("notifications-count");
    if (!el) return;
    var count = parseInt(el.textContent, 10) || 0;
    count = increment ? count + 1 : Math.max(0, count - 1);
    el.textContent = count;
    el.classList.toggle("hidden", count === 0);
}

/** Show the "No notifications yet" line if the list became empty. */
function showEmptyNotificationsMessage(list) {
    if (list.querySelector("li[data-id]")) return;
    var empty = document.createElement("li");
    empty.className = "px-4 py-3 text-muted-fg text-sm";
    empty.textContent = "No notifications yet";
    list.appendChild(empty);
}

/**
 * Build the list item of a notification: its message, age, and buttons to
 * mark it as read, open its page (if it has one) and delete it.
 */
function buildNotificationItem(notification) {
    var id = escapeHtml(notification.id);
    var cardClass = NOTIFICATION_STYLES[notification.type] || NOTIFICATION_STYLES.failed;
    var buttons = "";
    if (!notification.read) {
        buttons += "<button class=\"mark-read-btn btn btn-xs btn-secondary\" data-id=\"" + id + "\" type=\"button\">Mark as Read</button>";
    }
    if (notification.url) {
        buttons += "<a href=\"" + escapeHtml(notification.url) + "\" class=\"btn btn-xs btn-secondary\">Open</a>";
    }
    buttons += "<button class=\"delete-notif-btn btn btn-xs btn-danger hover:bg-danger-muted cursor-pointer\" data-id=\"" + id + "\" type=\"button\">Delete</button>";

    var li = document.createElement("li");
    li.className = "px-4 py-3 border-b border-border";
    li.setAttribute("data-id", notification.id);
    li.setAttribute("data-read", notification.read);
    li.innerHTML =
        "<div class=\"flex flex-col p-2 rounded-lg border-2 " + cardClass + "\">" +
        "<div class=\"notification-text " + (notification.read ? "" : "font-bold") + "\" data-id=\"" + id + "\">" + escapeHtml(notification.message) + "</div>" +
        "<div class=\"text-xs text-muted-fg mt-1\">" + timeAgo(notification.timestamp) + "</div>" +
        "<div class=\"mt-2 flex flex-wrap gap-2\">" + buttons + "</div>" +
        "</div>";
    return li;
}

/**
 * Add a notification at the top of the navbar list.
 */
function addNotification(notification) {
    var list = document.getElementById("notifications-list");
    if (!list) return;
    // Remove the "No notifications yet" line
    if (!list.querySelector("li[data-id]")) list.innerHTML = "";

    list.insertBefore(buildNotificationItem(notification), list.firstChild);
    if (!notification.read) changeNotificationCount(true);
}

/**
 * Handle a notification pushed by the server: show it as a toast and list it.
 */
function processNotification(notification) {
    var toastType = { success: "success", failed: "danger" }[notification.type] || "info";
    showToast("New Notification", notification.message, toastType);
    addNotification(notification);
}

/** Send a notification action ("mark_read" or "delete") to the server. */
function postNotificationAction(action, notificationId) {
    var formData = new FormData();
    formData.append("notification_id", notificationId);
    return fetch("/notifications/" + action, { method: "POST", body: formData });
}

/** Mark a notification as read, on the server and in the list. */
function markNotificationRead(notificationId) {
    postNotificationAction("mark_read", notificationId).then(function () {
        var li = document.querySelector("#notifications-list li[data-id=\"" + CSS.escape(notificationId) + "\"]");
        if (!li) return;
        li.setAttribute("data-read", "true");
        var text = li.querySelector(".notification-text");
        if (text) text.classList.remove("font-bold");
        var btn = li.querySelector(".mark-read-btn");
        if (btn) btn.remove();
        changeNotificationCount(false);
    });
}

/** Remove a notification from the list (updating the unread count). */
function deleteNotification(notificationId) {
    var list = document.getElementById("notifications-list");
    if (!list) return;
    var li = list.querySelector("li[data-id=\"" + CSS.escape(notificationId) + "\"]");
    if (li) {
        if (li.getAttribute("data-read") === "false") changeNotificationCount(false);
        li.remove();
    }
    showEmptyNotificationsMessage(list);
}

/**
 * Handle the list buttons with a single delegated listener, so items added
 * later don't need their own listeners.
 */
function bindNotificationsList() {
    var list = document.getElementById("notifications-list");
    if (!list) return;
    list.addEventListener("click", function (e) {
        var markReadBtn = e.target.closest(".mark-read-btn");
        if (markReadBtn) {
            markNotificationRead(markReadBtn.getAttribute("data-id"));
            return;
        }
        var deleteBtn = e.target.closest(".delete-notif-btn");
        if (deleteBtn) {
            var id = deleteBtn.getAttribute("data-id");
            postNotificationAction("delete", id).then(function () { deleteNotification(id); });
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindNotificationsList);
} else {
    bindNotificationsList();
}
