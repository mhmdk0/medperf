import pytest

from medperf import config
from medperf.exceptions import CleanExit
from medperf.web_ui import common
from medperf.web_ui.common import UITask

PATCH_COMMON = "medperf.web_ui.common.{}"


@pytest.fixture
def task_env(mocker):
    ui = mocker.patch.object(config, "ui")
    init = mocker.patch(PATCH_COMMON.format("initialize_state_task"))
    reset = mocker.patch(PATCH_COMMON.format("reset_state_task"))
    return ui, init, reset


def run_task(error=None):
    """Run a UITask whose block raises `error` (if given) and return it."""
    with UITask(object(), "my_task") as task:
        if error is not None:
            raise error
    return task


def test_successful_block_marks_task_as_succeeded(task_env):
    # Arrange
    ui, init, reset = task_env
    request = object()

    # Act
    with UITask(request, "my_task", response={"entity_id": None}) as task:
        task.response["entity_id"] = 5

    # Assert
    init.assert_called_once_with(request, task_name="my_task")
    assert task.succeeded
    assert task.response == {"status": "success", "error": "", "entity_id": 5}
    ui.end_task.assert_called_once_with(task.response)
    reset.assert_called_once_with(request)


def test_failing_block_is_reported_and_not_propagated(task_env, mocker):
    # Arrange
    ui, _, reset = task_env
    spy_exception = mocker.spy(common.logger, "exception")

    # Act
    task = run_task(ValueError("boom"))

    # Assert
    assert not task.succeeded
    assert task.response == {"status": "failed", "error": "boom"}
    spy_exception.assert_called_once()
    ui.end_task.assert_called_once_with(task.response)
    reset.assert_called_once()


def test_clean_exit_stops_the_task_without_error(task_env, mocker):
    # Arrange
    ui, _, reset = task_env
    spy_exception = mocker.spy(common.logger, "exception")

    # Act
    task = run_task(CleanExit("Dataset submission operation cancelled"))

    # Assert
    assert task.response == {
        "status": "info",
        "error": "Dataset submission operation cancelled",
    }
    spy_exception.assert_not_called()
    ui.end_task.assert_called_once_with(task.response)
    reset.assert_called_once()


def test_clean_exit_with_error_code_is_a_failure(task_env):
    # Act
    task = run_task(CleanExit(medperf_status_code=1))

    # Assert
    assert task.response["status"] == "failed"


def test_non_exception_errors_end_the_task_but_propagate(task_env):
    # Arrange
    ui, _, reset = task_env

    # Act & Assert
    with pytest.raises(KeyboardInterrupt):
        run_task(KeyboardInterrupt())
    ui.end_task.assert_called_once()
    reset.assert_called_once()


@pytest.mark.parametrize(
    "error, expected_message",
    [
        (None, "It worked"),
        (ValueError("boom"), "It failed"),
        (
            CleanExit("No users in need of keys were found."),
            "No users in need of keys were found.",
        ),
    ],
)
def test_notify_uses_the_message_of_the_outcome(task_env, error, expected_message):
    # Arrange
    ui, _, _ = task_env
    task = run_task(error)

    # Act
    task.notify("It worked", "It failed", url="/x")

    # Assert
    ui.add_notification.assert_called_once_with(
        message=expected_message, return_response=task.response, url="/x"
    )
