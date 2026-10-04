import pytest

from medperf.ui.web_ui import WebUI
from medperf.web_ui.history import TaskRecorder, WebUIHistoryStore, get_history_scope
from medperf.web_ui.schemas import GlobalEventsManager, Notification


PATCH_HISTORY = "medperf.web_ui.history.{}"
PATCH_WEB_UI = "medperf.ui.web_ui.{}"


@pytest.fixture
def store():
    store = WebUIHistoryStore(":memory:", max_notifications=3, max_tasks=2)
    yield store
    store.close()


def make_notification(id, timestamp, read=False):
    return Notification(
        id=id, message=f"msg {id}", type="success", read=read, timestamp=timestamp
    )


def make_task(id, finished_at):
    return {
        "id": id,
        "name": "some_task",
        "status": "success",
        "error": None,
        "started_at": finished_at - 1,
        "finished_at": finished_at,
        "logs": ["line 1", "line 2"],
    }


class TestWebUIHistoryStore:
    def test_saved_notifications_are_loaded_oldest_first(self, store):
        store.save_notification(make_notification("b", 2))
        store.save_notification(make_notification("a", 1))

        loaded = store.load_notifications()

        assert [n.id for n in loaded] == ["a", "b"]
        assert loaded[0].message == "msg a"

    def test_only_most_recent_notifications_are_kept(self, store):
        for i in range(5):
            store.save_notification(make_notification(str(i), i))

        assert [n.id for n in store.load_notifications()] == ["2", "3", "4"]

    def test_notification_can_be_marked_read_and_deleted(self, store):
        store.save_notification(make_notification("a", 1))
        store.save_notification(make_notification("b", 2))

        store.mark_notification_read("a")
        store.delete_notification("b")

        loaded = store.load_notifications()
        assert [(n.id, n.read) for n in loaded] == [("a", True)]

    def test_only_most_recent_tasks_are_kept(self, store):
        for i in range(4):
            store.save_task(make_task(str(i), i + 10))

        loaded = store.load_tasks()

        assert [t["id"] for t in loaded] == ["2", "3"]
        assert loaded[0]["logs"] == ["line 1", "line 2"]


class TestHistoryScope:
    def test_each_profile_and_user_only_sees_its_own_history(self, store):
        # Arrange
        store.set_scope("default", "alice@example.com")
        store.save_notification(make_notification("a", 1))
        store.save_task(make_task("task-a", 10))

        # Act
        store.set_scope("default", "bob@example.com")
        store.save_notification(make_notification("b", 2))

        # Assert
        assert [n.id for n in store.load_notifications()] == ["b"]
        assert store.load_tasks() == []
        store.set_scope("default", "alice@example.com")
        assert [n.id for n in store.load_notifications()] == ["a"]
        assert [t["id"] for t in store.load_tasks()] == ["task-a"]

    def test_limits_apply_per_scope(self, store):
        # Arrange
        store.set_scope("default", "alice@example.com")
        store.save_notification(make_notification("a", 1))
        store.set_scope("other", "alice@example.com")

        # Act
        for i in range(5):
            store.save_notification(make_notification(str(i), i + 10))

        # Assert
        assert [n.id for n in store.load_notifications()] == ["2", "3", "4"]
        store.set_scope("default", "alice@example.com")
        assert [n.id for n in store.load_notifications()] == ["a"]

    def test_scope_is_the_active_profile_and_its_user(self, mocker):
        # Arrange
        config_p = mocker.MagicMock(active_profile_name="default")
        mocker.patch(PATCH_HISTORY.format("read_config"), return_value=config_p)
        mocker.patch(
            PATCH_HISTORY.format("read_user_account"),
            return_value={"email": "alice@example.com"},
        )

        # Act & Assert
        assert get_history_scope() == ("default", "alice@example.com")

    def test_scope_email_is_empty_when_logged_out(self, mocker):
        # Arrange
        config_p = mocker.MagicMock(active_profile_name="default")
        mocker.patch(PATCH_HISTORY.format("read_config"), return_value=config_p)
        mocker.patch(PATCH_HISTORY.format("read_user_account"), return_value=None)

        # Act & Assert
        assert get_history_scope() == ("default", "")

    def test_web_ui_loads_the_history_of_the_new_scope(self, mocker, store):
        # Arrange
        scope = mocker.patch(
            PATCH_WEB_UI.format("get_history_scope"),
            return_value=("default", "alice@example.com"),
        )
        ui = WebUI()
        ui.attach_history_store(store)
        ui.add_notification("Alice's task finished", {"status": "success"})
        ui.start_task("t1", "benchmark_registration")
        ui.end_task({"status": "success"})

        # Act
        scope.return_value = ("default", "bob@example.com")
        ui.load_history()

        # Assert
        assert ui.get_all_notifications() == []
        assert ui.get_finished_tasks() == []


class TestTaskRecorder:
    def test_records_only_lines_of_the_running_task(self):
        recorder = TaskRecorder(max_tasks=5, max_log_lines=10)
        recorder.start("task-1", "benchmark_registration")

        recorder.record("task-1", "\x1b[31mfirst\x1b[0m")
        recorder.record("other-task", "ignored")
        recorder.record(None, "ignored too")
        recorder.record("task-1", "   ")
        recorder.finish({"status": "failed", "error": "boom"})

        [task] = recorder.get_finished_tasks()
        assert task["name"] == "benchmark_registration"
        assert task["logs"] == ["first"]
        assert task["status"] == "failed"
        assert task["error"] == "boom"

    def test_keeps_only_the_last_log_lines(self):
        recorder = TaskRecorder(max_tasks=5, max_log_lines=2)
        recorder.start("t", "task")
        for i in range(4):
            recorder.record("t", f"line {i}")
        recorder.finish({"status": "success"})

        assert recorder.get_finished_tasks()[0]["logs"] == ["line 2", "line 3"]

    def test_keeps_only_the_most_recent_tasks_most_recent_first(self):
        recorder = TaskRecorder(max_tasks=2, max_log_lines=10)
        for i in range(3):
            recorder.start(str(i), "task")
            recorder.finish({"status": "success"})

        assert [t["id"] for t in recorder.get_finished_tasks()] == ["2", "1"]

    def test_finish_without_running_task_does_nothing(self):
        recorder = TaskRecorder()

        recorder.finish({"status": "success"})

        assert recorder.get_finished_tasks() == []

    def test_finished_tasks_are_saved_and_reloaded(self, store):
        recorder = TaskRecorder()
        recorder.attach_store(store)
        recorder.start("t", "task")
        recorder.record("t", "hello")
        recorder.finish({"status": "success"})

        new_recorder = TaskRecorder()
        new_recorder.attach_store(store)

        [task] = new_recorder.get_finished_tasks()
        assert task["id"] == "t"
        assert task["logs"] == ["hello"]

    def test_storage_failure_does_not_raise(self, mocker):
        broken_store = mocker.Mock()
        broken_store.load_tasks.return_value = []
        broken_store.save_task.side_effect = Exception("disk full")
        recorder = TaskRecorder()
        recorder.attach_store(broken_store)
        recorder.start("t", "task")

        recorder.finish({"status": "success"})

        assert recorder.get_finished_tasks()[0]["id"] == "t"


class TestGlobalEventsManagerPersistence:
    def test_notifications_are_persisted_and_reloaded(self, store):
        manager = GlobalEventsManager()
        manager.attach_store(store)
        manager.add_notification("Done", {"status": "success"}, url="/x")
        notification = manager.get_new_notification()
        manager.mark_notification_as_read(notification.id)

        new_manager = GlobalEventsManager()
        new_manager.attach_store(store)

        [loaded] = new_manager.get_all_notifications()
        assert loaded.id == notification.id
        assert loaded.read is True
        assert loaded.url == "/x"
        # Restored notifications are not shown again as new ones
        assert new_manager.get_new_notification() is None

    def test_deleted_notifications_are_removed_from_store(self, store):
        manager = GlobalEventsManager()
        manager.attach_store(store)
        manager.add_notification("One", {"status": "success"}, url="")
        manager.add_notification("Two", {"status": "success"}, url="")
        first = manager.get_new_notification()

        manager.delete_notification(first.id)
        assert [n.message for n in store.load_notifications()] == ["Two"]

    def test_in_memory_notifications_are_capped(self):
        manager = GlobalEventsManager()
        manager.max_notifications = 2
        for i in range(3):
            manager.add_notification(f"n{i}", {"status": "success"}, url="")

        assert [n.message for n in manager.get_all_notifications()] == ["n1", "n2"]

    def test_works_without_store(self):
        manager = GlobalEventsManager()

        manager.add_notification("n", {"status": "success"}, url="")
        notification = manager.get_new_notification()
        manager.mark_notification_as_read(notification.id)
        manager.delete_notification(notification.id)

        assert manager.get_all_notifications() == []


def test_web_ui_records_task_output_without_a_browser_streaming():
    ui = WebUI()

    ui.start_task("task-1", "dataset_registration")
    ui.print("Preparing")
    ui.print_error("It failed")
    ui.end_task({"status": "failed", "error": "It failed"})

    [task] = ui.get_finished_tasks()
    assert task["name"] == "dataset_registration"
    assert task["logs"] == ["Preparing", "❌ It failed"]
    assert task["status"] == "failed"
