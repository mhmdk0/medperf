import threading
from collections import deque

import pytest

from medperf import config
from medperf.exceptions import CleanExit
from medperf.ui.web_ui import WebUI
from medperf.web_ui.containers.routes import grant_access_worker

PATCH_ROUTES = "medperf.web_ui.containers.routes.{}"
BENCHMARK_ID = 1
MODEL_ID = 2
EMAILS = "alice@example.com"


@pytest.fixture
def stop_event():
    return threading.Event()


@pytest.fixture
def web_ui(mocker):
    ui = WebUI()
    mocker.patch.object(config, "ui", ui)
    return ui


def run_grant_access_once(mocker, stop_event, side_effect):
    """Run the worker for a single iteration: the patched GrantAccess.run
    stops the worker before returning/raising."""

    def grant_access(**kwargs):
        stop_event.set()
        return side_effect()

    run = mocker.patch(PATCH_ROUTES.format("GrantAccess.run"), side_effect=grant_access)
    logs = deque()
    grant_access_worker(BENCHMARK_ID, MODEL_ID, EMAILS, 5, stop_event, logs)
    return run, [line.split("] ", 1)[1] for line in logs]


def test_grant_access_worker_runs_grant_access_with_given_args(
    mocker, web_ui, stop_event
):
    # Act
    run, _ = run_grant_access_once(mocker, stop_event, lambda: None)

    # Assert
    run.assert_called_once_with(
        benchmark_id=BENCHMARK_ID,
        model_id=MODEL_ID,
        approved=True,
        allowed_emails=EMAILS,
    )


def test_grant_access_worker_logs_captured_messages(mocker, web_ui, stop_event):
    # Arrange
    def grant_access():
        config.ui.print("Uploading Encrypted Keys")

    # Act
    _, logs = run_grant_access_once(mocker, stop_event, grant_access)

    # Assert
    assert logs == ["Uploading Encrypted Keys"]


def test_grant_access_worker_logs_clean_exit_as_message(mocker, web_ui, stop_event):
    # Arrange
    def grant_access():
        raise CleanExit("No users in need of keys were found.")

    spy_exception = mocker.patch(PATCH_ROUTES.format("logger.exception"))

    # Act
    _, logs = run_grant_access_once(mocker, stop_event, grant_access)

    # Assert
    assert logs == ["No users in need of keys were found."]
    spy_exception.assert_not_called()


def test_grant_access_worker_logs_errors(mocker, web_ui, stop_event):
    # Arrange
    def grant_access():
        raise ValueError("server unreachable")

    spy_exception = mocker.patch(PATCH_ROUTES.format("logger.exception"))

    # Act
    _, logs = run_grant_access_once(mocker, stop_event, grant_access)

    # Assert
    assert logs == ["Error: server unreachable"]
    spy_exception.assert_called_once()
