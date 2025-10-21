from medperf.web_ui.tests import config as tests_config
from medperf.web_ui.tests.pages.login_page import LoginPage
import pytest
import medperf.web_ui.events as events_module
from email_validator import EmailNotValidError
from unittest.mock import ANY

BASE_URL = tests_config.BASE_URL
EMAIL = "test@test.com"
PATCH_ROUTE = "medperf.web_ui.medperf_login.{}"


def fake_event_generator(*args, **kwargs):
    yield ""


@pytest.fixture()
def patch_common(mocker):
    init = mocker.patch(PATCH_ROUTE.format("initialize_state_task"), return_value=None)
    reset = mocker.patch(PATCH_ROUTE.format("reset_state_task"), return_value=None)
    notifs = mocker.patch(PATCH_ROUTE.format("add_notification"), return_value=None)

    return {
        "init_spy": init,
        "reset_spy": reset,
        "notifs_spy": notifs,
    }


def test_login_page_content(driver):
    page = LoginPage(driver)
    page.open(BASE_URL.format("/medperf_login"))
    page.wait_for_presence_selector(page.FORM)

    assert page.get_text(page.HEADER) == "Login"

    page.wait_for_presence_selector(page.EMAIL)
    page.wait_for_presence_selector(page.LOGIN)

    assert page.get_text(page.EMAIL_LABEL) == "Email"


def test_login_page_already_logged_in(mocker, driver, patch_common, ui):
    test_email = "test_email@test.com"
    error_msg = f"You are already logged in as {test_email}."
    read_acc = mocker.patch(
        PATCH_ROUTE.format("read_user_account"), return_value={"email": test_email}
    )
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)

    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = LoginPage(driver)
    page.open(BASE_URL.format("/medperf_login"))

    confirm_modal = page.find(page.CONFIRM_MODAL)
    error_modal = page.find(page.ERROR_MODAL)
    page.login(EMAIL)
    page.wait_for_visibility_element(confirm_modal)

    assert EMAIL in page.get_text(page.CONFIRM_TEXT)

    page.confirm_run_task()
    page.wait_for_visibility_element(error_modal)
    page.wait_for_presence_selector(page.ERROR_TITLE)
    page.wait_for_presence_selector(page.ERROR_TEXT)
    page.wait_for_presence_selector(page.ERROR_RELOAD)
    page.wait_for_presence_selector(page.ERROR_HIDE)

    assert page.get_text(page.ERROR_TITLE) == "Login Failed"
    assert error_msg in page.get_text(page.ERROR_TEXT)

    error_modal.find_element(*page.ERROR_HIDE).click()
    page.wait_for_invisibility_element(error_modal)

    patch_common["init_spy"].assert_called_with(ANY, task_name="medperf_login")
    spy_task_id.assert_called_once()
    read_acc.assert_called_once()
    event_gen.assert_called_once()
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()


def test_login_page_invalid_email(mocker, driver, patch_common, ui):
    error_msg = "Email not valid"
    read_acc = mocker.patch(PATCH_ROUTE.format("read_user_account"), return_value=None)
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    patch_email = mocker.patch(
        PATCH_ROUTE.format("validate_email"), side_effect=EmailNotValidError(error_msg)
    )
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = LoginPage(driver)
    page.open(BASE_URL.format("/medperf_login"))

    confirm_modal = page.find(page.CONFIRM_MODAL)
    error_modal = page.find(page.ERROR_MODAL)
    page.login(EMAIL)
    page.wait_for_visibility_element(confirm_modal)

    assert EMAIL in page.get_text(page.CONFIRM_TEXT)

    page.confirm_run_task()
    page.wait_for_visibility_element(error_modal)
    page.wait_for_presence_selector(page.ERROR_TITLE)
    page.wait_for_presence_selector(page.ERROR_TEXT)
    page.wait_for_presence_selector(page.ERROR_RELOAD)
    page.wait_for_presence_selector(page.ERROR_HIDE)

    assert page.get_text(page.ERROR_TITLE) == "Login Failed"
    assert error_msg in page.get_text(page.ERROR_TEXT)

    error_modal.find_element(*page.ERROR_HIDE).click()
    page.wait_for_invisibility_element(error_modal)

    patch_common["init_spy"].assert_called_once()
    spy_task_id.assert_called_once()
    read_acc.assert_called_once()
    patch_email.assert_called_with(EMAIL, check_deliverability=ANY)
    event_gen.assert_called_once()
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()


def test_login_page_success(mocker, driver, patch_common, ui, auth):
    read_acc = mocker.patch(PATCH_ROUTE.format("read_user_account"), return_value=None)
    patch_email = mocker.patch(PATCH_ROUTE.format("validate_email"), return_value=None)
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    auth.login = mocker.Mock()

    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = LoginPage(driver)
    page.open(BASE_URL.format("/medperf_login"))

    confirm_modal = page.find(page.CONFIRM_MODAL)
    popup_modal = page.find(page.POPUP_MODAL)
    page.login(EMAIL)
    page.wait_for_visibility_element(confirm_modal)

    assert EMAIL in page.get_text(page.CONFIRM_TEXT)

    current_url = page.current_url
    page.confirm_run_task()
    page.wait_for_visibility_element(popup_modal)

    assert page.get_text(page.POPUP_TITLE) == "Successfully Logged In"

    page.wait_for_url_change(current_url)

    patch_common["init_spy"].assert_called_once()
    spy_task_id.assert_called_once()
    read_acc.assert_called_once()
    patch_email.assert_called_once()
    auth.login.assert_called_with(EMAIL)
    event_gen.assert_called_once()
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()
