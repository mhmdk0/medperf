from unittest.mock import ANY
from medperf.web_ui.tests.pages.benchmark.details_page import BenchmarkDetailsPage
from medperf.tests.mocks.benchmark import TestBenchmark
from medperf.tests.mocks.cube import TestCube
from medperf.web_ui.app import web_app
import medperf.web_ui.tests.config as tests_config
import medperf.web_ui.events as events_module
import pytest
import datetime
from selenium.common.exceptions import NoSuchElementException
import json

BASE_URL = tests_config.BASE_URL
PATCH_BMK = "medperf.entities.benchmark.Benchmark.{}"
PATCH_EXECUTION = "medperf.entities.execution.Execution.{}"
PATCH_CONTAINER = "medperf.entities.cube.Cube.get"
PATCH_ROUTE = "medperf.web_ui.benchmarks.routes.{}"

TEST_CONTAINERS = [
    TestCube(
        id=1, name="data-prep", modified_at=datetime.datetime(2025, 10, 10), owner=1
    ),
    TestCube(
        id=2, name="ref-model", modified_at=datetime.datetime(2025, 10, 11), owner=1
    ),
    TestCube(
        id=3, name="metrics", modified_at=datetime.datetime(2025, 10, 12), owner=1
    ),
]
TEST_BENCHMARK = TestBenchmark(
    id=1,
    owner=1,
    name="test_benchmark",
    state="OPERATION",
    is_valid=True,
    data_preparation_mlcube=1,
    reference_model_mlcube=2,
    data_evaluator_mlcube=3,
    created_at=datetime.datetime(2025, 10, 15),
    modified_at=datetime.datetime(2025, 10, 17),
)


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


def get_fake_cube(cube_uid):
    return TEST_CONTAINERS[cube_uid - 1]


def fake_event_generator(*args, **kwargs):
    yield ""


@pytest.mark.parametrize("owner", [TEST_BENCHMARK.owner, TEST_BENCHMARK.owner + 1])
def Xtest_benchmark_details_page_content(driver, mocker, owner):
    patch_bmk = mocker.patch(PATCH_BMK.format("get"), return_value=TEST_BENCHMARK)
    patch_dsets_assocs = mocker.patch(
        PATCH_BMK.format("get_datasets_associations"), return_value=[]
    )
    patch_models_assocs = mocker.patch(
        PATCH_BMK.format("get_models_associations"), return_value=[]
    )
    patch_results = mocker.patch(PATCH_EXECUTION.format("all"), return_value=[])
    patch_get_datasets_with_users = mocker.patch(
        PATCH_BMK.format("get_datasets_with_users"), return_value=[]
    )

    patch_container = mocker.patch(PATCH_CONTAINER, side_effect=get_fake_cube)
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"), return_value={"id": owner}
    )

    page = BenchmarkDetailsPage(driver, benchmark=TEST_BENCHMARK.name)
    page.open(BASE_URL.format("/benchmarks/ui/display/") + str(TEST_BENCHMARK.id))

    page.wait_for_presence_selector(page.HEADER)
    page.wait_for_presence_selector(page.SUB_HEADER_1)

    page.wait_for_presence_selector(page.STATE)
    page.wait_for_presence_selector(page.VALID)

    page.wait_for_presence_selector(page.ID_LABEL)
    page.wait_for_presence_selector(page.ID)

    page.wait_for_presence_selector(page.DESCRIPTION_LABEL)
    page.wait_for_presence_selector(page.DESCRIPTION)

    page.wait_for_presence_selector(page.DOCUMENTATION_LABEL)
    page.wait_for_presence_selector(page.DOCUMENTATION)

    page.wait_for_presence_selector(page.REF_DATASET_LABEL)
    page.wait_for_presence_selector(page.REF_DATASET)

    page.wait_for_presence_selector(page.DATA_PREP_LABEL)
    page.wait_for_presence_selector(page.DATA_PREP)

    page.wait_for_presence_selector(page.REF_MODEL_LABEL)
    page.wait_for_presence_selector(page.REF_MODEL)

    page.wait_for_presence_selector(page.METRICS_LABEL)
    page.wait_for_presence_selector(page.METRICS)

    page.wait_for_presence_selector(page.OWNER_LABEL)
    page.wait_for_presence_selector(page.OWNER)

    page.wait_for_presence_selector(page.CREATED_LABEL)
    page.wait_for_presence_selector(page.CREATED)

    page.wait_for_presence_selector(page.MODIFIED_LABEL)
    page.wait_for_presence_selector(page.MODIFIED)

    if owner == TEST_BENCHMARK.owner:
        page.wait_for_presence_selector(page.SUB_HEADER_2)
        page.wait_for_presence_selector(page.POLICY_FORM)

        page.wait_for_presence_selector(page.DSET_AUTO_APPROVE_LABEL)
        page.wait_for_presence_selector(page.DSET_AUTO_APPROVE)
        page.wait_for_presence_selector(page.DSET_ALLOW_LIST_CONTAINER)
        page.wait_for_presence_selector(page.DSET_ALLOW_LIST_EMAILS)
        page.wait_for_presence_selector(page.DSET_ALLOW_LIST_LABEL)
        page.wait_for_presence_selector(page.DSET_ALLOW_LIST)

        page.wait_for_presence_selector(page.CONT_AUTO_APPROVE_LABEL)
        page.wait_for_presence_selector(page.CONT_AUTO_APPROVE)
        page.wait_for_presence_selector(page.CONT_ALLOW_LIST_CONTAINER)
        page.wait_for_presence_selector(page.CONT_ALLOW_LIST_EMAILS)
        page.wait_for_presence_selector(page.CONT_ALLOW_LIST_LABEL)
        page.wait_for_presence_selector(page.CONT_ALLOW_LIST)

        page.wait_for_presence_selector(page.SAVE)

        page.wait_for_presence_selector(page.DATASETS_TITLE)
        page.wait_for_presence_selector(page.DATASETS_ASSOCIATIONS)

        page.wait_for_presence_selector(page.MODELS_TITLE)
        page.wait_for_presence_selector(page.MODELS_ASSOCIATIONS)

        page.wait_for_presence_selector(page.RESULTS_TITLE)
        page.wait_for_presence_selector(page.RESULTS)

    page.wait_for_presence_selector(page.RESULT_MODAL)

    assert page.get_text(page.HEADER) == TEST_BENCHMARK.name
    assert page.get_text(page.SUB_HEADER_1) == "Details"

    if TEST_BENCHMARK.state == "OPERATION":
        assert page.get_text(page.STATE) == "OPERATIONAL"
        assert "badge-state-operational" in page.find(page.STATE).get_attribute("class")
    else:
        assert page.get_text(page.STATE) == TEST_BENCHMARK.state
        assert "badge-state-development" in page.find(page.STATE).get_attribute("class")

    if TEST_BENCHMARK.is_valid:
        assert page.get_text(page.VALID) == "VALID"
        assert "badge-valid" in page.find(page.VALID).get_attribute("class")
    else:
        assert page.get_text(page.VALID) == "INVALID"
        assert "badge-invalid" in page.find(page.VALID).get_attribute("class")

    assert page.get_text(page.ID_LABEL) == "Benchmark ID:"
    assert page.get_text(page.ID) == str(TEST_BENCHMARK.id)

    assert page.get_text(page.DESCRIPTION_LABEL) == "Description:"
    assert page.get_text(page.DESCRIPTION) == str(TEST_BENCHMARK.description)
    assert page.get_text(page.DOCUMENTATION_LABEL) == "Documentation:"

    if TEST_BENCHMARK.docs_url:
        assert page.get_text(page.DOCUMENTATION) == TEST_BENCHMARK.docs_url
        assert (
            page.find(page.DOCUMENTATION).get_attribute("href")
            == TEST_BENCHMARK.docs_url
        )
        assert page.find(page.DOCUMENTATION).get_attribute("target") == "_blank"
    else:
        assert page.get_text(page.DOCUMENTATION) == "Not Available"

    assert page.get_text(page.REF_DATASET_LABEL) == "Reference Dataset Tarball:"
    assert page.get_text(page.REF_DATASET) == "Click to Download the File"
    assert TEST_BENCHMARK.demo_dataset_tarball_url in page.find(
        page.REF_DATASET
    ).get_attribute("href")
    assert page.find(page.REF_DATASET).get_attribute("target") == "_blank"

    assert page.get_text(page.DATA_PREP_LABEL) == "Data Preparation Container:"
    assert page.get_text(page.DATA_PREP) == TEST_CONTAINERS[0].name
    assert (
        f"/containers/ui/display/{TEST_BENCHMARK.data_preparation_mlcube}"
        in page.find(page.DATA_PREP).get_attribute("href")
    )
    data_prep_date = page.find(page.DATA_PREP_DATE).get_attribute("data-date")
    assert (
        datetime.datetime.strptime(data_prep_date, "%Y-%m-%d %H:%M:%S")
        == TEST_CONTAINERS[0].modified_at
    )
    assert "fa-check-circle text-success" in page.find(
        page.DATA_PREP_STATE
    ).get_attribute("class")

    assert page.get_text(page.REF_MODEL_LABEL) == "Reference Model Container:"
    assert page.get_text(page.REF_MODEL) == TEST_CONTAINERS[1].name
    assert (
        f"/containers/ui/display/{TEST_BENCHMARK.reference_model_mlcube}"
        in page.find(page.REF_MODEL).get_attribute("href")
    )
    ref_model_date = page.find(page.REF_MODEL_DATE).get_attribute("data-date")
    assert (
        datetime.datetime.strptime(ref_model_date, "%Y-%m-%d %H:%M:%S")
        == TEST_CONTAINERS[1].modified_at
    )
    assert "fa-check-circle text-success" in page.find(
        page.REF_MODEL_STATE
    ).get_attribute("class")

    assert page.get_text(page.METRICS_LABEL) == "Metrics Container:"
    assert page.get_text(page.METRICS) == TEST_CONTAINERS[2].name
    assert (
        f"/containers/ui/display/{TEST_BENCHMARK.data_evaluator_mlcube}"
        in page.find(page.METRICS).get_attribute("href")
    )
    metrics_date = page.find(page.METRICS_DATE).get_attribute("data-date")
    assert (
        datetime.datetime.strptime(metrics_date, "%Y-%m-%d %H:%M:%S")
        == TEST_CONTAINERS[2].modified_at
    )
    assert "fa-check-circle text-success" in page.find(
        page.METRICS_STATE
    ).get_attribute("class")

    assert page.get_text(page.OWNER_LABEL) == "Owner:"
    assert page.get_text(page.OWNER) == str(TEST_BENCHMARK.owner)

    assert page.get_text(page.CREATED_LABEL) == "Created:"

    bmk_created = page.find(page.CREATED).get_attribute("data-date")
    assert (
        datetime.datetime.strptime(bmk_created, "%Y-%m-%d %H:%M:%S")
        == TEST_BENCHMARK.created_at
    )
    assert page.get_text(page.MODIFIED_LABEL) == "Modified:"

    bmk_modified = page.find(page.MODIFIED).get_attribute("data-date")
    assert (
        datetime.datetime.strptime(bmk_modified, "%Y-%m-%d %H:%M:%S")
        == TEST_BENCHMARK.modified_at
    )

    if owner == TEST_BENCHMARK.owner:
        assert page.get_text(page.SUB_HEADER_2) == "Association Policy"

        assert (
            page.get_text(page.DSET_AUTO_APPROVE_LABEL) == "Dataset auto approve mode"
        )
        page.select_by_text(page.DSET_AUTO_APPROVE, "Allow List")
        assert page.get_text(page.DSET_ALLOW_LIST_LABEL) == "Allow list emails"

        assert page.get_text(page.CONT_AUTO_APPROVE_LABEL) == "Model auto approve mode"
        page.select_by_text(page.CONT_AUTO_APPROVE, "Allow List")
        assert page.get_text(page.CONT_ALLOW_LIST_LABEL) == "Allow list emails"

        dataset_assocs_count = page.get_text(page.DATASETS_ASSOCS_COUNT)
        assert dataset_assocs_count == "0"
        assert (
            page.get_text(page.DATASETS_TITLE).strip(dataset_assocs_count).strip()
            == "Datasets Associations"
        )
        with pytest.raises(NoSuchElementException):
            page.driver.find_element(*page.DATASETS_PENDING_ASSOCS)

        model_assocs_count = page.get_text(page.MODELS_ASSOCS_COUNT)
        assert model_assocs_count == "0"
        assert (
            page.get_text(page.MODELS_TITLE).strip(model_assocs_count).strip()
            == "Models Associations"
        )
        with pytest.raises(NoSuchElementException):
            page.driver.find_element(*page.MODELS_PENDING_ASSOCS)

        results_count = page.get_text(page.RESULTS_COUNT)
        assert results_count == "0"
        assert (
            page.get_text(page.RESULTS_TITLE).strip(results_count).strip() == "Results"
        )

        filters = {"benchmark": TEST_BENCHMARK.id}

        patch_dsets_assocs.assert_called_once_with(benchmark_uid=TEST_BENCHMARK.id)
        patch_models_assocs.assert_called_once_with(benchmark_uid=TEST_BENCHMARK.id)
        patch_results.assert_called_once_with(filters=filters)
        patch_get_datasets_with_users.assert_called_once_with(TEST_BENCHMARK.id)
    else:
        patch_dsets_assocs.assert_not_called()
        patch_models_assocs.assert_not_called()
        patch_results.assert_not_called()
        patch_get_datasets_with_users.assert_not_called()

    patch_bmk.assert_called_with(TEST_BENCHMARK.id)
    assert patch_container.call_count == 3


@pytest.mark.parametrize(
    "mode", [{"text": "Never", "value": "NEVER"}, {"text": "Always", "value": "ALWAYS"}]
)
def Xtest_benchmark_details_dataset_auto_approve_mode(
    driver, mocker, mode, ui, patch_common
):
    mocker.patch(PATCH_BMK.format("get"), return_value=TEST_BENCHMARK)
    mocker.patch(PATCH_BMK.format("get_datasets_associations"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_models_associations"), return_value=[])
    mocker.patch(PATCH_EXECUTION.format("all"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_datasets_with_users"), return_value=[])
    mocker.patch(PATCH_CONTAINER, side_effect=get_fake_cube)
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"),
        return_value={"id": TEST_BENCHMARK.owner},
    )
    update_policy_patch = mocker.patch(
        PATCH_ROUTE.format("UpdateAssociationsPolicy.run"), return_value=None
    )

    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = BenchmarkDetailsPage(driver, benchmark=TEST_BENCHMARK.name)
    page.open(BASE_URL.format("/benchmarks/ui/display/") + str(TEST_BENCHMARK.id))

    model_mode_text = driver.find_element(
        "xpath", '//*[@id="model-auto-approve-mode"]/option[@selected]'
    ).text
    model_mode_value = page.find(page.CONT_AUTO_APPROVE).get_attribute("value")
    confirm_modal = page.find(page.CONFIRM_MODAL)
    popup_modal = page.find(page.POPUP_MODAL)
    page.select_by_text(page.DSET_AUTO_APPROVE, mode["text"])
    page.click(page.SAVE)
    page.wait_for_visibility_element(confirm_modal)

    assert f"Datasets: {mode['text']}" in page.get_text(page.CONFIRM_TEXT)
    assert f"Models: {model_mode_text}" in page.get_text(page.CONFIRM_TEXT)

    page.confirm_run_task()
    page.wait_for_visibility_element(popup_modal)

    assert (
        page.get_text(page.POPUP_TITLE)
        == "Benchmark Associations Policy Successfully Updated"
    )

    page.wait_for_staleness_element(popup_modal)

    patch_common["init_spy"].assert_called_once_with(
        ANY, task_name="update_associations_policy"
    )
    spy_task_id.assert_called_once()
    update_policy_patch.assert_called_once_with(
        benchmark_uid=TEST_BENCHMARK.id,
        dataset_mode=mode["value"],
        dataset_emails=None,
        model_mode=model_mode_value,
        model_emails=None,
    )
    event_gen.assert_not_called()
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()


@pytest.mark.parametrize("emails", [[], ["test@test.com", "test1@test.com"]])
def Xtest_benchmark_details_dataset_auto_approve_mode_allow_list_emails(
    driver, mocker, emails, approve_mode="ALLOWLIST"
):
    mocker.patch(PATCH_BMK.format("get"), return_value=TEST_BENCHMARK)
    mocker.patch(PATCH_BMK.format("get_datasets_associations"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_models_associations"), return_value=[])
    mocker.patch(PATCH_EXECUTION.format("all"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_datasets_with_users"), return_value=[])
    mocker.patch(PATCH_CONTAINER, side_effect=get_fake_cube)
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"),
        return_value={"id": TEST_BENCHMARK.owner},
    )

    TEST_BENCHMARK.dataset_auto_approval_allow_list = emails
    TEST_BENCHMARK.dataset_auto_approval_mode = approve_mode

    page = BenchmarkDetailsPage(driver, benchmark=TEST_BENCHMARK.name)
    page.open(BASE_URL.format("/benchmarks/ui/display/") + str(TEST_BENCHMARK.id))

    assert page.find(page.DSET_AUTO_APPROVE).get_attribute("value") == approve_mode

    dataset_emails_container = page.find(page.DSET_ALLOW_LIST_EMAILS)
    dataset_emails = dataset_emails_container.get_attribute("data-allowed-list")

    assert json.loads(dataset_emails) == emails
    emails_chips = dataset_emails_container.find_elements(*page.EMAIL_CHIP)
    assert len(emails_chips) == len(emails)
    for email_chip in emails_chips:
        remove_btn = email_chip.find_element(*page.REMOVE_EMAIL)
        assert email_chip.text.strip(remove_btn.text) in emails
        page.ensure_element_ready(remove_btn)
        remove_btn.click()
    emails_chips = dataset_emails_container.find_elements(*page.EMAIL_CHIP)
    assert len(emails_chips) == 0


@pytest.mark.parametrize(
    "emails",
    [
        "test@test.com,",
        "test@test.com ",
        "test@test.com,test1@test.com,test2@test.com,",
        "test@test.com test1@test.com test2@test.com ",
    ],
)
def Xtest_benchmark_details_dataset_auto_approve_mode_allow_list_emails_input(
    driver, mocker, emails, approve_mode="Allow List"
):
    mocker.patch(PATCH_BMK.format("get"), return_value=TEST_BENCHMARK)
    mocker.patch(PATCH_BMK.format("get_datasets_associations"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_models_associations"), return_value=[])
    mocker.patch(PATCH_EXECUTION.format("all"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_datasets_with_users"), return_value=[])
    mocker.patch(PATCH_CONTAINER, side_effect=get_fake_cube)
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"),
        return_value={"id": TEST_BENCHMARK.owner},
    )

    page = BenchmarkDetailsPage(driver, benchmark=TEST_BENCHMARK.name)
    page.open(BASE_URL.format("/benchmarks/ui/display/") + str(TEST_BENCHMARK.id))

    page.select_by_text(page.DSET_AUTO_APPROVE, approve_mode)
    page.type(page.DSET_ALLOW_LIST, emails)

    dataset_emails_container = page.find(page.DSET_ALLOW_LIST_EMAILS)
    emails_chips = dataset_emails_container.find_elements(*page.EMAIL_CHIP)
    emails_parts = emails.split(",") if "," in emails else emails.split(" ")
    emails_list = [i.strip() for i in emails_parts if i.strip()]

    assert len(emails_chips) == len(emails_list)

    for email_chip in emails_chips:
        remove_btn = email_chip.find_element(*page.REMOVE_EMAIL)
        assert email_chip.text.strip(remove_btn.text) in emails
        page.ensure_element_ready(remove_btn)
        remove_btn.click()
    emails_chips = dataset_emails_container.find_elements(*page.EMAIL_CHIP)
    assert len(emails_chips) == 0


def test_benchmark_details_dataset_auto_approve_mode_allow_list_emails_input_submit(
    driver,
    mocker,
    ui,
    patch_common,
    approve_mode=["Allow List", "ALLOWLIST"],
    emails="test@test.com test1@test.com ",
):
    mocker.patch(PATCH_BMK.format("get"), return_value=TEST_BENCHMARK)
    mocker.patch(PATCH_BMK.format("get_datasets_associations"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_models_associations"), return_value=[])
    mocker.patch(PATCH_EXECUTION.format("all"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_datasets_with_users"), return_value=[])
    mocker.patch(PATCH_CONTAINER, side_effect=get_fake_cube)
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"),
        return_value={"id": TEST_BENCHMARK.owner},
    )
    update_policy_patch = mocker.patch(
        PATCH_ROUTE.format("UpdateAssociationsPolicy.run"), return_value=None
    )
    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = BenchmarkDetailsPage(driver, benchmark=TEST_BENCHMARK.name)
    page.open(BASE_URL.format("/benchmarks/ui/display/") + str(TEST_BENCHMARK.id))

    model_mode_text = driver.find_element(
        "xpath", '//*[@id="model-auto-approve-mode"]/option[@selected]'
    ).text
    model_mode_value = page.find(page.CONT_AUTO_APPROVE).get_attribute("value")
    confirm_modal = page.find(page.CONFIRM_MODAL)
    popup_modal = page.find(page.POPUP_MODAL)

    page.select_by_text(page.DSET_AUTO_APPROVE, approve_mode[0])
    page.type(page.DSET_ALLOW_LIST, emails)
    page.click(page.SAVE)

    page.wait_for_visibility_element(confirm_modal)

    assert f"Datasets: {approve_mode[0]}" in page.get_text(page.CONFIRM_TEXT)
    assert f"Models: {model_mode_text}" in page.get_text(page.CONFIRM_TEXT)

    page.confirm_run_task()
    page.wait_for_visibility_element(popup_modal)

    assert (
        page.get_text(page.POPUP_TITLE)
        == "Benchmark Associations Policy Successfully Updated"
    )

    page.wait_for_staleness_element(popup_modal)

    patch_common["init_spy"].assert_called_once_with(
        ANY, task_name="update_associations_policy"
    )
    spy_task_id.assert_called_once()
    update_policy_patch.assert_called_once_with(
        benchmark_uid=TEST_BENCHMARK.id,
        dataset_mode=approve_mode[1],
        dataset_emails=emails.strip(),
        model_mode=model_mode_value,
        model_emails=None,
    )
    event_gen.assert_not_called()
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()


@pytest.mark.parametrize(
    "mode", [{"text": "Never", "value": "NEVER"}, {"text": "Always", "value": "ALWAYS"}]
)
def Xtest_benchmark_details_model_auto_approve_mode(
    driver, mocker, mode, ui, patch_common
):
    mocker.patch(PATCH_BMK.format("get"), return_value=TEST_BENCHMARK)
    mocker.patch(PATCH_BMK.format("get_datasets_associations"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_models_associations"), return_value=[])
    mocker.patch(PATCH_EXECUTION.format("all"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_datasets_with_users"), return_value=[])
    mocker.patch(PATCH_CONTAINER, side_effect=get_fake_cube)
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"),
        return_value={"id": TEST_BENCHMARK.owner},
    )
    update_policy_patch = mocker.patch(
        PATCH_ROUTE.format("UpdateAssociationsPolicy.run"), return_value=None
    )

    event_gen = mocker.patch.object(
        events_module, "event_generator", side_effect=fake_event_generator
    )
    ui.task_id = "test-id"
    ui.end_task = mocker.Mock(return_value=None)
    ui.get_event = mocker.Mock(return_value=None)
    spy_task_id = mocker.spy(events_module, "_get_task_id")

    page = BenchmarkDetailsPage(driver, benchmark=TEST_BENCHMARK.name)
    page.open(BASE_URL.format("/benchmarks/ui/display/") + str(TEST_BENCHMARK.id))

    dataset_mode_text = driver.find_element(
        "xpath", '//*[@id="dataset-auto-approve-mode"]/option[@selected]'
    ).text
    dataset_mode_value = page.find(page.DSET_AUTO_APPROVE).get_attribute("value")
    confirm_modal = page.find(page.CONFIRM_MODAL)
    popup_modal = page.find(page.POPUP_MODAL)
    page.select_by_text(page.CONT_AUTO_APPROVE, mode["text"])
    page.click(page.SAVE)
    page.wait_for_visibility_element(confirm_modal)

    assert f"Datasets: {dataset_mode_text}" in page.get_text(page.CONFIRM_TEXT)
    assert f"Models: {mode['text']}" in page.get_text(page.CONFIRM_TEXT)

    page.confirm_run_task()
    page.wait_for_visibility_element(popup_modal)

    assert (
        page.get_text(page.POPUP_TITLE)
        == "Benchmark Associations Policy Successfully Updated"
    )

    page.wait_for_staleness_element(popup_modal)

    patch_common["init_spy"].assert_called_once_with(
        ANY, task_name="update_associations_policy"
    )
    spy_task_id.assert_called_once()
    update_policy_patch.assert_called_once_with(
        benchmark_uid=TEST_BENCHMARK.id,
        dataset_mode=dataset_mode_value,
        dataset_emails=None,
        model_mode=mode["value"],
        model_emails=None,
    )
    event_gen.assert_not_called()
    ui.end_task.assert_called_once()
    patch_common["reset_spy"].assert_called_once()
    patch_common["notifs_spy"].assert_called_once()


def Xtest_benchmark_details_model_auto_approve_mode_allow_list(driver, mocker):
    mocker.patch(PATCH_BMK.format("get"), return_value=TEST_BENCHMARK)
    mocker.patch(PATCH_BMK.format("get_datasets_associations"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_models_associations"), return_value=[])
    mocker.patch(PATCH_EXECUTION.format("all"), return_value=[])
    mocker.patch(PATCH_BMK.format("get_datasets_with_users"), return_value=[])
    mocker.patch(PATCH_CONTAINER, side_effect=get_fake_cube)
    mocker.patch(
        PATCH_ROUTE.format("get_medperf_user_data"),
        return_value={"id": TEST_BENCHMARK.owner},
    )
    update_policy_patch = mocker.patch(
        PATCH_ROUTE.format("UpdateAssociationsPolicy.run"), return_value=None
    )

    page = BenchmarkDetailsPage(driver, benchmark=TEST_BENCHMARK.name)
    page.open(BASE_URL.format("/benchmarks/ui/display/") + str(TEST_BENCHMARK.id))


def Xtest_benchmark_details_dataset_associations_pending(driver, mocker):
    pass


def Xtest_benchmark_details_models_associations_pending(driver, mocker):
    pass


def Xtest_benchmark_details_results_not_submitted(driver, mocker):
    pass


def Xtest_benchmark_details_results_submitted(driver, mocker):
    pass


def Xtest_benchmark_registration_page_task_running(driver, mocker):
    web_app.state.task_running = True
