from medperf.web_ui.tests import config as tests_config
from medperf.web_ui.tests.pages.container.details_page import ContainerDetailsPage

import datetime
import pytest
from unittest.mock import ANY
from medperf.tests.mocks.cube import TestCube
from medperf.tests.mocks.benchmark import TestBenchmark
import medperf.web_ui.events as events_module
from medperf.web_ui.app import web_app
from selenium.common.exceptions import NoSuchElementException


def get_date_string():
    return (
        datetime.datetime(2025, 10, 17, tzinfo=datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


BASE_URL = tests_config.BASE_URL
PATCH_GET_BENCHMARKS = "medperf.entities.benchmark.Benchmark.all"
PATCH_CONTAINER = "medperf.entities.cube.Cube.{}"
PATCH_ROUTE = "medperf.web_ui.containers.routes.{}"

TEST_CONTAINER = TestCube(
    id=10,
    owner=1,
    name="test_container",
    created_at=datetime.datetime(2025, 10, 15),
    modified_at=datetime.datetime(2025, 10, 17),
)

BENCHMARKS_ASSOCS = {
    "1": {
        "id": 1,
        "metadata": {"key1": "value1", "key2": "value2"},
        "approval_status": "APPROVED",
        "approved_at": get_date_string(),
        "created_at": get_date_string(),
        "modified_at": get_date_string(),
        "priority": 0,
        "model_mlcube": 1,
        "benchmark": 1,
        "initiated_by": 1,
    },
    "2": {
        "id": 2,
        "metadata": {"key1": "value1", "key2": "value2"},
        "approval_status": "REJECTED",
        "approved_at": get_date_string(),
        "created_at": get_date_string(),
        "modified_at": get_date_string(),
        "priority": 0,
        "model_mlcube": 1,
        "benchmark": 2,
        "initiated_by": 1,
    },
    "3": {
        "id": 3,
        "metadata": {"key1": "value1", "key2": "value2"},
        "approval_status": "PENDING",
        "approved_at": get_date_string(),
        "created_at": get_date_string(),
        "modified_at": get_date_string(),
        "priority": 0,
        "model_mlcube": 1,
        "benchmark": 3,
        "initiated_by": 1,
    },
}

TEST_BENCHMARKS = {
    "1": TestBenchmark(
        id=1,
        owner=10,
        name="test_benchmark",
        created_at=datetime.datetime(2025, 10, 15),
        modified_at=datetime.datetime(2025, 10, 17),
    ),
    "2": TestBenchmark(
        id=2,
        owner=30,
        name="test_benchmark",
        created_at=datetime.datetime(2025, 10, 15),
        modified_at=datetime.datetime(2025, 10, 17),
    ),
    "3": TestBenchmark(
        id=3,
        owner=30,
        name="test_benchmark",
        created_at=datetime.datetime(2025, 10, 15),
        modified_at=datetime.datetime(2025, 10, 17),
    ),
}

BENCHMARK_TO_ASSOCIATE = TEST_BENCHMARKS["2"]


def stub_event_generator(*args, **kwargs):
    yield ""


@pytest.fixture()
def patch_container_details_empty_assocs(mocker):
    spy_container = mocker.patch(
        PATCH_CONTAINER.format("get"), return_value=TEST_CONTAINER
    )
    spy_benchmarks_assocs = mocker.patch(
        PATCH_CONTAINER.format("get_benchmarks_associations"), return_value=[]
    )

    spy_benchmarks = mocker.patch(PATCH_GET_BENCHMARKS, return_value=[])

    return (spy_container, spy_benchmarks_assocs, spy_benchmarks)


@pytest.fixture()
def patch_container_details_assocs(mocker):
    spy_container = mocker.patch(
        PATCH_CONTAINER.format("get"), return_value=TEST_CONTAINER
    )
    spy_benchmarks_assocs = mocker.patch(
        PATCH_CONTAINER.format("get_benchmarks_associations"),
        return_value=list(BENCHMARKS_ASSOCS.values()),
    )

    spy_benchmarks = mocker.patch(
        PATCH_GET_BENCHMARKS, return_value=list(TEST_BENCHMARKS.values())
    )

    return (spy_container, spy_benchmarks_assocs, spy_benchmarks)


@pytest.fixture()
def patch_owner(mocker):
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"),
        return_value={"id": TEST_CONTAINER.owner},
    )


@pytest.fixture()
def patch_common(mocker):
    init = mocker.patch(PATCH_ROUTE.format("initialize_state_task"))
    reset = mocker.patch(PATCH_ROUTE.format("reset_state_task"))
    notifs = mocker.patch(PATCH_ROUTE.format("add_notification"))

    return (init, reset, notifs)


@pytest.fixture(scope="module")
def page(driver):
    return ContainerDetailsPage(driver)


@pytest.mark.parametrize("user", [TEST_CONTAINER.owner, TEST_CONTAINER.owner + 1])
def test_container_details_common_content(
    page, mocker, user, patch_container_details_empty_assocs
):
    mocker.patch(PATCH_ROUTE.format("get_medperf_user_data"), return_value={"id": user})

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    assert page.get_text(page.HEADER) == TEST_CONTAINER.name
    assert page.get_text(page.SUB_HEADER_1) == "Details"

    assert page.get_text(page.ID_LABEL) == "Container ID:"
    assert page.get_text(page.ID) == str(TEST_CONTAINER.id)

    manifest = page.find(page.MANIFEST)
    assert page.get_text(page.MANIFEST_LABEL) == "Container Manifest:"
    assert manifest.get_attribute("href") == TEST_CONTAINER.git_mlcube_url
    assert manifest.text == TEST_CONTAINER.git_mlcube_url

    parameters = page.find(page.PARAMETERS)
    assert page.get_text(page.PARAMETERS_LABEL) == "Parameters:"
    assert parameters.get_attribute("href") == TEST_CONTAINER.git_parameters_url
    assert parameters.text == TEST_CONTAINER.git_parameters_url

    assert page.get_text(page.OWNER_LABEL) == "Owner:"
    assert page.get_text(page.OWNER) == str(TEST_CONTAINER.owner)

    container_created = page.get_attribute(page.CREATED, "data-date")
    assert page.get_text(page.CREATED_LABEL) == "Created:"
    assert (
        datetime.datetime.strptime(container_created, "%Y-%m-%d %H:%M:%S")
        == TEST_CONTAINER.created_at
    )

    container_modified = page.get_attribute(page.MODIFIED, "data-date")
    assert page.get_text(page.MODIFIED_LABEL) == "Modified:"
    assert (
        datetime.datetime.strptime(container_modified, "%Y-%m-%d %H:%M:%S")
        == TEST_CONTAINER.modified_at
    )


@pytest.mark.parametrize("user", [TEST_CONTAINER.owner, TEST_CONTAINER.owner + 1])
def test_container_details_backend_calls(
    page, mocker, user, patch_container_details_empty_assocs
):
    spy_container, spy_benchmarks_assocs, spy_benchmarks = (
        patch_container_details_empty_assocs
    )

    mocker.patch(PATCH_ROUTE.format("get_medperf_user_data"), return_value={"id": user})

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    if TEST_CONTAINER.owner == user:
        spy_container.assert_called_once_with(
            cube_uid=TEST_CONTAINER.id, valid_only=ANY
        )
        spy_benchmarks_assocs.assert_called_once_with(mlcube_uid=TEST_CONTAINER.id)
        spy_benchmarks.assert_called_once()
    else:
        spy_container.assert_called_once_with(
            cube_uid=TEST_CONTAINER.id, valid_only=ANY
        )
        spy_benchmarks_assocs.assert_not_called()
        spy_benchmarks.assert_not_called()


def test_container_details_owner_content_loaded_for_owner(
    page, patch_container_details_empty_assocs, patch_owner
):
    spy_container, spy_benchmarks_assocs, spy_benchmarks = (
        patch_container_details_empty_assocs
    )

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    page.wait_for_presence_selector(page.ASSOCIATIONS_CONTAINER)

    dropdown_container = page.find(page.DROPDOWN_CONTAINER)
    page.click(page.DROPDOWN_BTN)
    page.wait_for_visibility_element(dropdown_container)

    assert page.get_text(page.NO_BMKS) == "No benchmarks available for association"
    assert (
        page.get_text(page.NOTE)
        == "If this is a model container, make a request to the benchmark owner to associate your model with the benchmark"
    )
    assert page.get_text(page.SUB_HEADER_2) == "Associated Benchmarks"
    assert len(page.driver.find_elements(*page.BMKS_ASSOCIATIONS)) == 0


def test_container_details_owner_content_not_loaded_for_other_users(
    page, mocker, patch_container_details_empty_assocs
):
    spy_container, spy_benchmarks_assocs, spy_benchmarks = (
        patch_container_details_empty_assocs
    )
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"),
        return_value={"id": TEST_CONTAINER.owner + 1},
    )

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    with pytest.raises(NoSuchElementException):
        page.driver.find_element(*page.BOTTOM_BUTTONS_CONTAINER)

    with pytest.raises(NoSuchElementException):
        page.driver.find_element(*page.ASSOCIATIONS_CONTAINER)


@pytest.mark.parametrize("user", [TEST_CONTAINER.owner, TEST_CONTAINER.owner + 1])
@pytest.mark.parametrize("state", ["OPERATION", "DEVELOPMENT"])
def test_container_details_state(
    page, mocker, user, state, patch_container_details_empty_assocs
):
    TEST_CONTAINER.state = state

    mocker.patch(PATCH_ROUTE.format("get_medperf_user_data"), return_value={"id": user})

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    if TEST_CONTAINER.state == "OPERATION":
        assert page.get_text(page.STATE) == "OPERATIONAL"
        assert "badge-state-operational" in page.get_attribute(page.STATE, "class")
    else:
        assert page.get_text(page.STATE) == TEST_CONTAINER.state
        assert "badge-state-development" in page.get_attribute(page.STATE, "class")

    TEST_CONTAINER.state = "OPERATION"


@pytest.mark.parametrize("user", [TEST_CONTAINER.owner, TEST_CONTAINER.owner + 1])
@pytest.mark.parametrize("is_valid", [True, False])
def test_container_details_validity(
    page, mocker, user, is_valid, patch_container_details_empty_assocs
):
    TEST_CONTAINER.is_valid = is_valid

    mocker.patch(PATCH_ROUTE.format("get_medperf_user_data"), return_value={"id": user})

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    if TEST_CONTAINER.is_valid:
        assert page.get_text(page.VALID) == "VALID"
        assert "badge-valid" in page.get_attribute(page.VALID, "class")
    else:
        assert page.get_text(page.VALID) == "INVALID"
        assert "badge-invalid" in page.get_attribute(page.VALID, "class")

    TEST_CONTAINER.is_valid = True


@pytest.mark.parametrize("user", [TEST_CONTAINER.owner, TEST_CONTAINER.owner + 1])
@pytest.mark.parametrize("image_tarball_url", [None, "http://test.com/test.yaml"])
def test_container_details_image_tarball(
    page, mocker, user, image_tarball_url, patch_container_details_empty_assocs
):
    TEST_CONTAINER.image_tarball_url = image_tarball_url

    mocker.patch(PATCH_ROUTE.format("get_medperf_user_data"), return_value={"id": user})

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    assert page.get_text(page.TARBALL_LABEL) == "Image Tarball:"

    if TEST_CONTAINER.image_tarball_url:
        tarball = page.find(page.TARBALL)
        assert tarball.get_attribute("href") == TEST_CONTAINER.image_tarball_url
        assert tarball.get_attribute("target") == "_blank"
        assert tarball.text == "Click to Download the File"
        with pytest.raises(NoSuchElementException):
            page.driver.find_element(*page.NO_TARBALL)
    else:
        assert page.get_text(page.NO_TARBALL) == "Not Available"
        with pytest.raises(NoSuchElementException):
            page.driver.find_element(*page.TARBALL)

    TEST_CONTAINER.image_tarball_url = "None"


@pytest.mark.parametrize("user", [TEST_CONTAINER.owner, TEST_CONTAINER.owner + 1])
@pytest.mark.parametrize("additional_files", [None, "http://test.com/test.yaml"])
def test_container_details_additional_tarball(
    page, mocker, user, additional_files, patch_container_details_empty_assocs
):
    TEST_CONTAINER.additional_files_tarball_url = additional_files

    mocker.patch(PATCH_ROUTE.format("get_medperf_user_data"), return_value={"id": user})

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    assert page.get_text(page.ADDITIONAL_LABEL) == "Additional Files:"

    if TEST_CONTAINER.additional_files_tarball_url:
        additional = page.find(page.ADDITIONAL)
        assert (
            additional.get_attribute("href")
            == TEST_CONTAINER.additional_files_tarball_url
        )
        assert additional.get_attribute("target") == "_blank"
        assert additional.text == "Click to Download the File"
        with pytest.raises(NoSuchElementException):
            page.driver.find_element(*page.NO_ADDITIONAL)
    else:
        assert page.get_text(page.NO_ADDITIONAL) == "Not Available"
        with pytest.raises(NoSuchElementException):
            page.driver.find_element(*page.ADDITIONAL)

    TEST_CONTAINER.additional_files_tarball_url = None


def test_container_details_page_benchmarks_associations_dropdown_content(
    page, patch_container_details_assocs, patch_owner
):
    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    associable_benchmarks_count = 0
    associations = [a["benchmark"] for a in BENCHMARKS_ASSOCS.values()]
    for benchmark in TEST_BENCHMARKS.values():
        benchmark_id = benchmark.id
        if benchmark.id not in associations or benchmark.id in [
            a["benchmark"]
            for a in BENCHMARKS_ASSOCS.values()
            if a["approval_status"] == "REJECTED"
        ]:
            associable_benchmarks_count += 1

    dropdown_container = page.find(page.DROPDOWN_CONTAINER)
    page.click(page.DROPDOWN_BTN)
    page.wait_for_visibility_element(dropdown_container)
    associations_items = dropdown_container.find_elements(
        "css selector", "li.dropdown-item"
    )

    assert len(associations_items) == associable_benchmarks_count

    for item in associations_items:
        bmk_data = item.find_element(*page.BMK_DATA).text
        bmk_view = item.find_element(*page.BMK_VIEW)
        bmk_associate = item.find_element(*page.BMK_ASSOCIATE)

        benchmark_id = bmk_associate.get_attribute("data-benchmark-id")
        container_id = bmk_associate.get_attribute("data-container-id")

        assert bmk_data == f"{benchmark_id} - {TEST_BENCHMARKS[benchmark_id].name}"
        assert f"/benchmarks/ui/display/{benchmark_id}" in bmk_view.get_attribute(
            "href"
        )
        assert bmk_view.text == "View Benchmark"
        assert bmk_associate.text == "Request Association"
        assert container_id == str(TEST_CONTAINER.id)

    with pytest.raises(NoSuchElementException):
        dropdown_container.find_element(*page.NO_BMKS)


def test_container_details_page_benchmarks_associations_content(
    page, patch_container_details_assocs, patch_owner
):
    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    benchmarks_associations = page.find_elements(page.BMKS_ASSOCIATIONS)
    assert len(benchmarks_associations) == len(BENCHMARKS_ASSOCS)

    for assoc in benchmarks_associations:
        assoc_id = assoc.get_attribute("data-testid")
        benchmark_anchor = assoc.find_element(*page.ASSOC_ANCHOR)
        approval_label = assoc.find_element(*page.ASSOC_APPROVAL_LABEL)
        page.wait_for_visibility_element(approval_label)
        approval = assoc.find_element(*page.ASSOC_APPROVAL).text
        approved_at_label = assoc.find_element(*page.ASSOC_APPROVED_AT_LABEL).text

        approved_at = assoc.find_element(*page.ASSOC_APPROVED_AT)
        modified_at_label = assoc.find_element(*page.ASSOC_MODIFIED_AT_LABEL).text
        modified_at = assoc.find_element(*page.ASSOC_MODIFIED_AT).get_attribute(
            "data-date"
        )
        initiated_by_label = assoc.find_element(*page.ASSOC_INITIATED_BY_LABEL).text
        initiated_by = assoc.find_element(*page.ASSOC_INITIATED_BY).text

        benchmark_name = assoc.find_element(*page.ASSOC_NAME).text
        benchmark_anchor_name = benchmark_anchor.text
        benchmark_anchor_url = benchmark_anchor.get_attribute("href")

        benchmark_id = str(BENCHMARKS_ASSOCS[assoc_id]["benchmark"])

        assert (
            benchmark_name
            == benchmark_anchor_name
            == TEST_BENCHMARKS[benchmark_id].name
        )
        assert f"/benchmarks/ui/display/{benchmark_id}" in benchmark_anchor_url
        assert approval_label.text == "Approval Status:"
        assert approved_at_label == "Approved:"
        assert modified_at_label == "Modified:"
        assert initiated_by_label == "Initiated By:"

        assert approval == BENCHMARKS_ASSOCS[assoc_id]["approval_status"]
        assert modified_at == BENCHMARKS_ASSOCS[assoc_id]["modified_at"]
        assert initiated_by == str(BENCHMARKS_ASSOCS[assoc_id]["initiated_by"])

        if BENCHMARKS_ASSOCS[assoc_id]["approval_status"] == "PENDING":
            assert approved_at.text == "N/A"
        else:
            approved_at_date = approved_at.get_attribute("data-date")
            assert approved_at_date == BENCHMARKS_ASSOCS[assoc_id]["approved_at"]
            if BENCHMARKS_ASSOCS[assoc_id]["approval_status"] == "REJECTED":
                assert "invalid-card" in assoc.get_attribute("class")


def test_container_details_request_association_fails(
    page, mocker, ui, patch_common, patch_container_details_assocs, patch_owner
):
    error_msg = "Request association test failed"

    spy_init, spy_reset, spy_notifs = patch_common
    spy_request_assoc = mocker.patch(
        PATCH_ROUTE.format("AssociateCube.run"), side_effect=Exception(error_msg)
    )
    spy_event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=stub_event_generator
    )
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    ui.end_task = mocker.Mock()
    ui.task_id = "test-id"

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    dropdown_container = page.find(page.DROPDOWN_CONTAINER)
    page.click(page.DROPDOWN_BTN)
    page.wait_for_visibility_element(dropdown_container)
    associations_items = dropdown_container.find_elements(
        "css selector", "li.dropdown-item"
    )
    bmk_associate = associations_items[0].find_element(*page.BMK_ASSOCIATE)

    confirm_modal = page.find(page.CONFIRM_MODAL)
    error_modal = page.find(page.ERROR_MODAL)

    page.ensure_element_ready(bmk_associate)
    bmk_associate.click()
    page.wait_for_invisibility_element(dropdown_container)
    page.wait_for_visibility_element(confirm_modal)

    page.confirm_run_task()
    page.wait_for_visibility_element(error_modal)
    page.wait_for_presence_selector(page.ERROR_RELOAD)

    assert page.get_text(page.ERROR_TITLE) == "Association Request Failed"
    assert error_msg in page.get_text(page.ERROR_TEXT)

    hide_btn = error_modal.find_element(*page.ERROR_HIDE)
    page.ensure_element_ready(hide_btn)
    hide_btn.click()

    page.wait_for_invisibility_element(error_modal)

    spy_init.assert_called_once_with(ANY, task_name="container_association")
    spy_event_gen.assert_called_once_with(request=ANY, stream_old=False)
    spy_request_assoc.assert_called_once_with(
        cube_uid=TEST_CONTAINER.id, benchmark_uid=BENCHMARK_TO_ASSOCIATE.id
    )

    spy_task_id.assert_called_once()
    spy_reset.assert_called_once()
    spy_notifs.assert_called_once()

    ui.end_task.assert_called_once()


def test_container_details_request_association_succeed(
    page, mocker, ui, patch_common, patch_container_details_assocs, patch_owner
):
    spy_init, spy_reset, spy_notifs = patch_common
    spy_request_assoc = mocker.patch(PATCH_ROUTE.format("AssociateCube.run"))
    spy_event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=stub_event_generator
    )
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    ui.end_task = mocker.Mock()
    ui.task_id = "test-id"

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    dropdown_container = page.find(page.DROPDOWN_CONTAINER)
    page.click(page.DROPDOWN_BTN)
    page.wait_for_visibility_element(dropdown_container)
    associations_items = dropdown_container.find_elements(
        "css selector", "li.dropdown-item"
    )
    bmk_associate = associations_items[0].find_element(*page.BMK_ASSOCIATE)

    confirm_modal = page.find(page.CONFIRM_MODAL)
    popup_modal = page.find(page.POPUP_MODAL)

    page.ensure_element_ready(bmk_associate)
    bmk_associate.click()
    page.wait_for_invisibility_element(dropdown_container)
    page.wait_for_visibility_element(confirm_modal)

    page.confirm_run_task()
    page.wait_for_visibility_element(popup_modal)

    assert page.get_text(page.POPUP_TITLE) == "Association Requested Successfully"

    page.wait_for_staleness_element(popup_modal)

    spy_init.assert_called_once_with(ANY, task_name="container_association")
    spy_event_gen.assert_called_once_with(request=ANY, stream_old=False)
    spy_request_assoc.assert_called_once_with(
        cube_uid=TEST_CONTAINER.id, benchmark_uid=BENCHMARK_TO_ASSOCIATE.id
    )

    spy_task_id.assert_called_once()
    spy_reset.assert_called_once()
    spy_notifs.assert_called_once()

    ui.end_task.assert_called_once()


def test_container_details_task_running(
    page, patch_container_details_assocs, patch_owner
):
    web_app.state.task_running = True
    web_app.state.task.running = True

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    assert not page.find(page.DROPDOWN_BTN).is_enabled()


def test_container_details_task_running_different_container(
    page, patch_container_details_assocs, patch_owner
):
    web_app.state.task_running = True
    web_app.state.task.running = True
    web_app.state.task.name = "container_association"
    web_app.state.task.formData = {"container_id": str(TEST_CONTAINER.id + 1)}

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    assert not page.find(page.DROPDOWN_BTN).is_enabled()

    with pytest.raises(NoSuchElementException):
        page.driver.find_element(*page.RESUME_SCRIPT)


def test_container_details_task_running_resume(
    page, mocker, ui, patch_container_details_assocs, patch_owner
):
    spy_event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=stub_event_generator
    )

    ui.end_task = mocker.Mock()
    ui.task_id = "test-id"

    web_app.state.task_running = True
    web_app.state.task.running = True
    web_app.state.task.name = "container_association"
    web_app.state.task.formData = {"container_id": str(TEST_CONTAINER.id)}

    page.open(BASE_URL.format(f"/containers/ui/display/{TEST_CONTAINER.id}"))

    associate_dropdown = page.find(page.DROPDOWN_BTN)

    assert not associate_dropdown.is_enabled()
    assert page.element_contains_spinner(associate_dropdown)

    page.find(page.RESUME_SCRIPT)

    spy_event_gen.assert_called_once_with(request=ANY, stream_old=True)
