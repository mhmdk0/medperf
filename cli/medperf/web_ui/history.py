"""Persistent history of the web UI.

Notifications and the logs of the most recent finished tasks are kept in a
local SQLite database, so they are not lost when the web UI is restarted.
"""

import json
import logging
import re
import sqlite3
import threading
import time
from typing import Dict, List, Optional

from medperf import config
from medperf.web_ui.schemas import Notification

logger = logging.getLogger(__name__)

_ANSI_ESCAPE_RE = re.compile(r"[\u001b\u009b][\[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]")


def strip_ansi(text: str) -> str:
    """Remove terminal color/style escape sequences from a string."""
    return _ANSI_ESCAPE_RE.sub("", text or "")


class WebUIHistoryStore:
    """SQLite-backed storage of web UI notifications and finished tasks.

    A single connection is shared between threads and guarded by a lock,
    which also allows using an in-memory database (":memory:") in tests.
    """

    def __init__(
        self,
        db_path: str,
        max_notifications: int = config.webui_max_saved_notifications,
        max_tasks: int = config.webui_max_saved_tasks,
    ):
        self.max_notifications = max_notifications
        self.max_tasks = max_tasks
        self._lock = threading.Lock()
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        with self._lock, self._db:
            self._db.execute(
                """CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    read INTEGER NOT NULL DEFAULT 0,
                    timestamp REAL NOT NULL,
                    url TEXT
                )"""
            )
            self._db.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error TEXT,
                    started_at REAL NOT NULL,
                    finished_at REAL NOT NULL,
                    logs TEXT NOT NULL
                )"""
            )

    # Notifications

    def save_notification(self, notification: Notification):
        with self._lock, self._db:
            self._db.execute(
                "INSERT OR REPLACE INTO notifications VALUES (?, ?, ?, ?, ?, ?)",
                (
                    notification.id,
                    notification.message,
                    notification.type,
                    int(notification.read),
                    notification.timestamp,
                    notification.url,
                ),
            )
            # Keep only the most recent notifications
            self._db.execute(
                """DELETE FROM notifications WHERE id NOT IN (
                    SELECT id FROM notifications ORDER BY timestamp DESC LIMIT ?
                )""",
                (self.max_notifications,),
            )

    def mark_notification_read(self, notification_id: str):
        with self._lock, self._db:
            self._db.execute(
                "UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,)
            )

    def delete_notification(self, notification_id: str):
        with self._lock, self._db:
            self._db.execute(
                "DELETE FROM notifications WHERE id = ?", (notification_id,)
            )

    def clear_notifications(self):
        with self._lock, self._db:
            self._db.execute("DELETE FROM notifications")

    def load_notifications(self) -> List[Notification]:
        """Return the saved notifications, oldest first."""
        with self._lock:
            rows = self._db.execute(
                "SELECT id, message, type, read, timestamp, url FROM notifications"
                " ORDER BY timestamp ASC"
            ).fetchall()
        return [
            Notification(
                id=row[0],
                message=row[1],
                type=row[2],
                read=bool(row[3]),
                timestamp=row[4],
                url=row[5],
            )
            for row in rows
        ]

    # Tasks

    def save_task(self, task: Dict):
        with self._lock, self._db:
            self._db.execute(
                "INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    task["id"],
                    task["name"],
                    task["status"],
                    task["error"],
                    task["started_at"],
                    task["finished_at"],
                    json.dumps(task["logs"]),
                ),
            )
            # Keep only the most recent tasks
            self._db.execute(
                """DELETE FROM tasks WHERE id NOT IN (
                    SELECT id FROM tasks ORDER BY finished_at DESC LIMIT ?
                )""",
                (self.max_tasks,),
            )

    def load_tasks(self) -> List[Dict]:
        """Return the saved tasks, oldest first."""
        with self._lock:
            rows = self._db.execute(
                "SELECT id, name, status, error, started_at, finished_at, logs"
                " FROM tasks ORDER BY finished_at ASC"
            ).fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "status": row[2],
                "error": row[3],
                "started_at": row[4],
                "finished_at": row[5],
                "logs": json.loads(row[6]),
            }
            for row in rows
        ]

    def close(self):
        with self._lock:
            self._db.close()


class TaskRecorder:
    """Records the output of the running web UI task, independently of whether
    a browser is currently streaming its events, and keeps the most recent
    finished tasks in memory (and in the history store, if one is attached).
    """

    def __init__(
        self,
        max_tasks: int = config.webui_max_saved_tasks,
        max_log_lines: int = config.webui_max_saved_task_log_lines,
    ):
        self.max_tasks = max_tasks
        self.max_log_lines = max_log_lines
        self.store: Optional[WebUIHistoryStore] = None
        self.finished_tasks: List[Dict] = []
        self._current: Optional[Dict] = None
        self._lock = threading.Lock()

    def attach_store(self, store: WebUIHistoryStore):
        """Use the given store for persistence and load the tasks saved in it."""
        with self._lock:
            self.store = store
            self.finished_tasks = store.load_tasks()[-self.max_tasks:]

    def start(self, task_id: str, task_name: str):
        with self._lock:
            self._current = {
                "id": task_id,
                "name": task_name,
                "status": "running",
                "error": None,
                "started_at": time.time(),
                "finished_at": None,
                "logs": [],
            }

    def record(self, task_id: Optional[str], message: str):
        """Add a log line to the running task (ignored if it belongs to another task)."""
        message = strip_ansi(message).strip()
        if not message:
            return
        with self._lock:
            if self._current is None or self._current["id"] != task_id:
                return
            logs = self._current["logs"]
            logs.append(message)
            if len(logs) > self.max_log_lines:
                del logs[: len(logs) - self.max_log_lines]

    def finish(self, response: Optional[dict]):
        """Mark the running task as finished and save it."""
        response = response or {}
        with self._lock:
            task = self._current
            self._current = None
            if task is None:
                return
            task["status"] = response.get("status") or "finished"
            task["error"] = response.get("error") or None
            task["finished_at"] = time.time()
            self.finished_tasks.append(task)
            if len(self.finished_tasks) > self.max_tasks:
                del self.finished_tasks[: len(self.finished_tasks) - self.max_tasks]
            store = self.store

        if store is not None:
            try:
                store.save_task(task)
            except Exception as e:
                logger.exception(f"Failed to save task {task['id']} to history: {e}")

    def get_finished_tasks(self) -> List[Dict]:
        """Return the finished tasks, most recent first."""
        with self._lock:
            return [dict(task) for task in reversed(self.finished_tasks)]
