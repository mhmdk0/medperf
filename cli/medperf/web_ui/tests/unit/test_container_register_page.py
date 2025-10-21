from unittest.mock import ANY
from medperf.web_ui.tests.pages.container.register_page import RegContainerPage
import pytest
from medperf.web_ui.app import web_app

from selenium.common.exceptions import NoSuchElementException
import medperf.web_ui.tests.config as tests_config
import medperf.web_ui.events as events_module

BASE_URL = tests_config.BASE_URL
PATCH_BENCHMARKS = "medperf.entities.cube.Cube.all"
PATCH_REGISTRATION = "medperf.commands.mlcube.submit.SubmitCube.run"
PATCH_ROUTE = "medperf.web_ui.containers.routes.{}"


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


def fake_event_generator(*args, **kwargs):
    yield ""


def test_container_registration_page_content(driver):
    page = RegContainerPage(driver)
    page.open(BASE_URL.format("/containers/register/ui"))

    page.wait_for_presence_selector(page.HEADER)

    page.wait_for_presence_selector(page.FORM)

    page.wait_for_presence_selector(page.NAME_LABEL)
    page.wait_for_presence_selector(page.NAME)
    page.wait_for_presence_selector(page.NAME_TOOLTIP)

    page.wait_for_presence_selector(page.MANIFEST_LABEL)
    page.wait_for_presence_selector(page.MANIFEST)
    page.wait_for_presence_selector(page.MANIFEST_TOOLTIP)

    page.wait_for_presence_selector(page.PARAMETERS_LABEL)
    page.wait_for_presence_selector(page.PARAMETERS)
    page.wait_for_presence_selector(page.PARAMETERS_TOOLTIP)

    page.wait_for_presence_selector(page.ADDITIONAL_LABEL)
    page.wait_for_presence_selector(page.ADDITIONAL)
    page.wait_for_presence_selector(page.ADDITIONAL_TOOLTIP)

    page.wait_for_presence_selector(page.REGISTER)

    page.wait_for_presence_selector(page.CONFIRM_MODAL)
    page.wait_for_presence_selector(page.ERROR_MODAL)
    page.wait_for_presence_selector(page.POPUP_MODAL)
    page.wait_for_presence_selector(page.TEXT_CONTAINER)
    page.wait_for_presence_selector(page.PROMPT_CONTAINER)

    assert page.get_text(page.HEADER) == "Register a New Container"
    assert page.get_text(page.NAME_LABEL) == "Container name"
    assert page.get_text(page.MANIFEST_LABEL) == "Container manifest file URL"
    assert page.get_text(page.PARAMETERS_LABEL) == "Parameters File URL"
    assert page.get_text(page.ADDITIONAL_LABEL) == "Additional Files URL"


def test_container_registration_page_tooltips(driver):
    page = RegContainerPage(driver)
    page.open(BASE_URL.format("/containers/register/ui"))

    name_tooltip = page.find(page.NAME_TOOLTIP)
    manifest_tooltip = page.find(page.MANIFEST_TOOLTIP)
    parameters_tooltip = page.find(page.PARAMETERS_TOOLTIP)
    additional_tooltip = page.find(page.ADDITIONAL_TOOLTIP)

    page.move_to_element(name_tooltip)
    tooltip_text = page.get_text(page.TOOLTIP)

    assert tooltip_text == "Name of the container you are registering"

    page.move_to_element(manifest_tooltip)
    tooltip_text = page.get_text(page.TOOLTIP)

    assert (
        tooltip_text == "URL of the manifest file for the container you are registering"
    )

    page.move_to_element(parameters_tooltip)
    tooltip_text = page.get_text(page.TOOLTIP)

    assert (
        tooltip_text
        == "URL of the parameters file for the container you are registering"
    )

    page.move_to_element(additional_tooltip)
    tooltip_text = page.get_text(page.TOOLTIP)

    assert (
        tooltip_text
        == "URL of the additional file for the container you are registering"
    )


def test_container_registration_fails(driver, mocker, ui, patch_common):
    error_message = "Error registering container."

    patch_register = mocker.patch(
        PATCH_REGISTRATION, side_effect=Exception(error_message)
    )
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = RegContainerPage(driver)
    page.open(BASE_URL.format("/containers/register/ui"))

    confirm_modal = page.find(page.CONFIRM_MODAL)
    error_modal = page.find(page.ERROR_MODAL)

    test_container = {
        "name": "test_container",
        "manifest": "test_manifest.yaml",
        "parameters": "",
        "additional": "",
    }

    page.register_container(test_container)

    page.wait_for_visibility_element(confirm_modal)
    page.confirm_run_task()

    page.wait_for_visibility_element(error_modal)
    page.wait_for_presence_selector(page.ERROR_TITLE)
    page.wait_for_presence_selector(page.ERROR_TEXT)
    page.wait_for_presence_selector(page.ERROR_RELOAD)
    page.wait_for_presence_selector(page.ERROR_HIDE)

    assert page.get_text(page.ERROR_TITLE) == "Failed to Register Model"
    assert error_message in page.get_text(page.ERROR_TEXT)

    error_modal.find_element(*page.ERROR_HIDE).click()
    page.wait_for_invisibility_element(error_modal)

    patch_common["init_spy"].assert_called_with(ANY, task_name="container_registration")
    spy_task_id.assert_called_once()
    event_gen.assert_called_with(request=ANY, stream_old=False)
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()
    container_info = {
        "name": test_container["name"],
        "git_mlcube_url": test_container["manifest"],
        "git_mlcube_hash": "",
        "git_parameters_url": test_container["parameters"],
        "parameters_hash": "",
        "image_tarball_url": "",
        "image_tarball_hash": "",
        "additional_files_tarball_url": test_container["additional"],
        "additional_files_tarball_hash": "",
        "state": "OPERATION",
    }
    patch_register.assert_called_with(container_info)


def test_container_registration_fails_with_optional(driver, mocker, ui, patch_common):
    error_message = "Error registering container."

    patch_register = mocker.patch(
        PATCH_REGISTRATION, side_effect=Exception(error_message)
    )
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = RegContainerPage(driver)
    page.open(BASE_URL.format("/containers/register/ui"))

    confirm_modal = page.find(page.CONFIRM_MODAL)
    error_modal = page.find(page.ERROR_MODAL)

    test_container = {
        "name": "test_container",
        "manifest": "test_manifest.yaml",
        "parameters": "test_parameters.yaml",
        "additional": "test_additional.yaml",
    }

    page.register_container(test_container)

    page.wait_for_visibility_element(confirm_modal)
    page.confirm_run_task()

    page.wait_for_visibility_element(error_modal)
    page.wait_for_presence_selector(page.ERROR_TITLE)
    page.wait_for_presence_selector(page.ERROR_TEXT)
    page.wait_for_presence_selector(page.ERROR_RELOAD)
    page.wait_for_presence_selector(page.ERROR_HIDE)

    assert page.get_text(page.ERROR_TITLE) == "Failed to Register Model"
    assert error_message in page.get_text(page.ERROR_TEXT)

    error_modal.find_element(*page.ERROR_HIDE).click()
    page.wait_for_invisibility_element(error_modal)

    patch_common["init_spy"].assert_called_with(ANY, task_name="container_registration")
    spy_task_id.assert_called_once()
    event_gen.assert_called_with(request=ANY, stream_old=False)
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()
    container_info = {
        "name": test_container["name"],
        "git_mlcube_url": test_container["manifest"],
        "git_mlcube_hash": "",
        "git_parameters_url": test_container["parameters"],
        "parameters_hash": "",
        "image_tarball_url": "",
        "image_tarball_hash": "",
        "additional_files_tarball_url": test_container["additional"],
        "additional_files_tarball_hash": "",
        "state": "OPERATION",
    }
    patch_register.assert_called_with(container_info)


def test_container_registration_succeed(driver, mocker, ui, patch_common):
    patch_register = mocker.patch(PATCH_REGISTRATION, return_value=1)
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = RegContainerPage(driver)
    page.open(BASE_URL.format("/containers/register/ui"))

    confirm_modal = page.find(page.CONFIRM_MODAL)
    popup_modal = page.find(page.POPUP_MODAL)

    test_container = {
        "name": "test_container",
        "manifest": "test_manifest.yaml",
        "parameters": "",
        "additional": "",
    }

    page.register_container(test_container)

    old_url = page.current_url
    page.wait_for_visibility_element(confirm_modal)
    page.confirm_run_task()

    page.wait_for_visibility_element(popup_modal)
    assert page.get_text(page.POPUP_TITLE) == "Model Registered Successfully"

    page.wait_for_url_change(old_url)
    assert "/containers/ui/display/1" in page.current_url

    patch_common["init_spy"].assert_called_with(ANY, task_name="container_registration")
    spy_task_id.assert_called_once()
    event_gen.assert_called_with(request=ANY, stream_old=False)
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()
    container_info = {
        "name": test_container["name"],
        "git_mlcube_url": test_container["manifest"],
        "git_mlcube_hash": "",
        "git_parameters_url": test_container["parameters"],
        "parameters_hash": "",
        "image_tarball_url": "",
        "image_tarball_hash": "",
        "additional_files_tarball_url": test_container["additional"],
        "additional_files_tarball_hash": "",
        "state": "OPERATION",
    }
    patch_register.assert_called_with(container_info)


def test_container_registration_succeed_with_optional(driver, mocker, ui, patch_common):
    patch_register = mocker.patch(PATCH_REGISTRATION, return_value=1)
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = RegContainerPage(driver)
    page.open(BASE_URL.format("/containers/register/ui"))

    confirm_modal = page.find(page.CONFIRM_MODAL)
    popup_modal = page.find(page.POPUP_MODAL)

    test_container = {
        "name": "test_container",
        "manifest": "test_manifest.yaml",
        "parameters": "test_parameters.yaml",
        "additional": "test_additional.yaml",
    }

    page.register_container(test_container)

    old_url = page.current_url
    page.wait_for_visibility_element(confirm_modal)
    page.confirm_run_task()

    page.wait_for_visibility_element(popup_modal)
    assert page.get_text(page.POPUP_TITLE) == "Model Registered Successfully"

    page.wait_for_url_change(old_url)
    assert "/containers/ui/display/1" in page.current_url

    patch_common["init_spy"].assert_called_with(ANY, task_name="container_registration")
    spy_task_id.assert_called_once()
    event_gen.assert_called_with(request=ANY, stream_old=False)
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()
    container_info = {
        "name": test_container["name"],
        "git_mlcube_url": test_container["manifest"],
        "git_mlcube_hash": "",
        "git_parameters_url": test_container["parameters"],
        "parameters_hash": "",
        "image_tarball_url": "",
        "image_tarball_hash": "",
        "additional_files_tarball_url": test_container["additional"],
        "additional_files_tarball_hash": "",
        "state": "OPERATION",
    }
    patch_register.assert_called_with(container_info)


def test_contianer_registration_page_task_running(driver, mocker, ui, patch_common):
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")
    web_app.state.task.running = True

    page = RegContainerPage(driver)
    page.open(BASE_URL.format("/containers/register/ui"))

    name = page.find(page.NAME)
    manifest = page.find(page.MANIFEST)
    parameters = page.find(page.PARAMETERS)
    additional = page.find(page.ADDITIONAL)

    assert not name.is_enabled()
    assert not manifest.is_enabled()
    assert not parameters.is_enabled()
    assert not additional.is_enabled()
    assert not page.find(page.REGISTER).is_enabled()

    assert name.get_attribute("value") == ""
    assert manifest.get_attribute("value") == ""
    assert parameters.get_attribute("value") == ""
    assert additional.get_attribute("value") == ""

    with pytest.raises(NoSuchElementException):
        page.driver.find_element(*page.RESUME_SCRIPT)

    patch_common["init_spy"].assert_not_called()
    spy_task_id.assert_not_called()
    event_gen.assert_not_called()
    ui.end_task.assert_not_called()
    patch_common["reset_spy"].assert_not_called()
    patch_common["notifs_spy"].assert_not_called()


def test_container_registration_page_task_running_form_data(
    driver, mocker, ui, patch_common
):
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    web_app.state.task_running = True
    web_app.state.task.running = True
    web_app.state.task.name = "container_registration"
    web_app.state.task.formData = {
        "name": "test_container",
        "container_file": "test_manifest.yaml",
        "parameters_file": "test_parameters.yaml",
        "additional_file": "test_additional.yaml",
    }

    page = RegContainerPage(driver)
    page.open(BASE_URL.format("/containers/register/ui"))

    name = page.find(page.NAME)
    manifest = page.find(page.MANIFEST)
    parameters = page.find(page.PARAMETERS)
    additional = page.find(page.ADDITIONAL)

    assert not name.is_enabled()
    assert not manifest.is_enabled()
    assert not parameters.is_enabled()
    assert not additional.is_enabled()
    assert not page.find(page.REGISTER).is_enabled()

    assert name.get_attribute("value") == "test_container"
    assert manifest.get_attribute("value") == "test_manifest.yaml"
    assert parameters.get_attribute("value") == "test_parameters.yaml"
    assert additional.get_attribute("value") == "test_additional.yaml"

    page.driver.find_element(*page.RESUME_SCRIPT)

    patch_common["init_spy"].assert_not_called()
    spy_task_id.assert_not_called()
    event_gen.assert_called_with(request=ANY, stream_old=True)
    ui.end_task.assert_not_called()
    patch_common["reset_spy"].assert_not_called()
    patch_common["notifs_spy"].assert_not_called()
