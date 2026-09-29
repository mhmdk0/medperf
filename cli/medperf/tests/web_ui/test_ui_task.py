import pytest

from medperf import config
from medperf.web_ui import common
from medperf.web_ui.common import UITask


@pytest.fixture
def task_env(mocker):
    ui = mocker.patch.object(config, "ui")
    init = mocker.patch.object(common, "initialize_state_task")
    reset = mocker.patch.object(common, "reset_state_task")
    return ui, init, reset


def test_successful_block_marks_task_as_succeeded(task_env):
    ui, init, reset = task_env
    request = object()

    with UITask(request, "my_task", response={"entity_id": None}) as task:
        task.response["entity_id"] = 5

    init.assert_called_once_with(request, task_name="my_task")
    assert task.succeeded
    assert task.response == {"status": "success", "error": "", "entity_id": 5}
    ui.end_task.assert_called_once_with(task.response)
    reset.assert_called_once_with(request)


def test_failing_block_is_reported_and_not_propagated(task_env):
    ui, _, reset = task_env

    with UITask(object(), "my_task") as task:
        raise ValueError("boom")

    assert not task.succeeded
    assert task.response == {"status": "failed", "error": "boom"}
    ui.end_task.assert_called_once_with(task.response)
    reset.assert_called_once()


def test_non_exception_errors_end_the_task_but_propagate(task_env):
    ui, _, reset = task_env

    with pytest.raises(KeyboardInterrupt):
        with UITask(object(), "my_task"):
            raise KeyboardInterrupt()

    ui.end_task.assert_called_once()
    reset.assert_called_once()


@pytest.mark.parametrize(
    "fail, expected_message", [(False, "It worked"), (True, "It failed")]
)
def test_notify_uses_the_message_of_the_outcome(task_env, fail, expected_message):
    ui, _, _ = task_env

    with UITask(object(), "my_task") as task:
        if fail:
            raise ValueError("boom")
    task.notify("It worked", "It failed", url="/x")

    ui.add_notification.assert_called_once_with(
        message=expected_message, return_response=task.response, url="/x"
    )
