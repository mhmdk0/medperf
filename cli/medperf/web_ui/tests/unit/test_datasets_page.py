import pytest
from medperf.web_ui.tests import config as tests_config
from medperf.web_ui.tests.pages.dataset.ui_page import DatasetsPage
from medperf.tests.mocks.dataset import TestDataset
import datetime
import selenium.common.exceptions as selenium_exceptions

BASE_URL = tests_config.BASE_URL
PATCH_GET_ALL_DSETS = "medperf.entities.dataset.Dataset.all"
PATCH_GET_USER_ID = "medperf.web_ui.datasets.routes.get_medperf_user_data"


def test_empty_datasets_ui_page_content(mocker, driver):
    mocker.patch(PATCH_GET_USER_ID, return_value={"id": 1})
    dsets_patch = mocker.patch(PATCH_GET_ALL_DSETS, return_value=[])
    filters = {"owner": 1}

    page = DatasetsPage(driver)
    page.open(BASE_URL.format("/datasets/ui"))

    dsets_patch.assert_called_with(filters={})
    assert page.get_text(page.REG_DSET_BTN) == "Register a New Dataset"
    assert page.get_text(page.IMPORT_DSET_BTN) == "Import Dataset"
    assert page.get_text(page.HEADER) == "Datasets"
    assert page.get_text(page.MINE_LABEL) == "Show only my datasets"
    assert page.get_text(page.NO_DATASETS) == "No datasets yet"
    assert page.find(page.MINE_SWITCH).get_attribute("data-entity-name") == "datasets"

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.is_mine()
    dsets_patch.assert_called_with(filters=filters)

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.not_mine()
    dsets_patch.assert_called_with(filters={})


def test_datasets_ui_page_content(mocker, driver):
    dset1 = TestDataset(id=1, owner=1, created_at=datetime.datetime(2025, 1, 1))
    dset2 = TestDataset(id=2, owner=2, created_at=datetime.datetime(2025, 5, 20))
    dset1.description = "Dataset sample"
    dset1.state = "DEVELOPMENT"
    dsets = [dset1, dset2]

    mocker.patch(PATCH_GET_USER_ID, return_value={"id": 1})
    mocker.patch(PATCH_GET_ALL_DSETS, return_value=dsets)

    page = DatasetsPage(driver)
    page.open(BASE_URL.format("/datasets/ui"))

    with pytest.raises(selenium_exceptions.NoSuchElementException):
        page.driver.find_element(*page.NO_DATASETS)

    dataset_cards = page.find_elements(page.CARDS_CONTAINER)

    assert len(dataset_cards) == len(dsets)

    for i in range(len(dsets)):
        dset_name = dataset_cards[i].find_element(*page.CARD_TITLE).text
        dset_url = dataset_cards[i].find_element(*page.CARD_TITLE).get_attribute("href")
        dset_id_txt = dataset_cards[i].find_element(*page.CARD_ID).text
        dset_state = dataset_cards[i].find_element(*page.CARD_STATE).text
        dset_valid_txt = dataset_cards[i].find_element(*page.CARD_VALID).text
        dset_desc_txt = dataset_cards[i].find_element(*page.CARD_DESC).text
        dset_created = (
            dataset_cards[i].find_element(*page.CARD_CREATED).get_attribute("data-date")
        )
        dset_location_txt = dataset_cards[i].find_element(*page.CARD_LOCATION).text

        dset_id = dset_id_txt.split(":")[-1].strip()
        dset_id_url = dset_url.split("/")[-1].strip()
        dset_valid = dset_valid_txt.split(":")[-1].strip()
        dset_desc = dset_desc_txt.split(":", 1)[-1].strip()
        dset_created_dt = datetime.datetime.strptime(dset_created, "%Y-%m-%d %H:%M:%S")
        dset_location = dset_location_txt.split(":")[-1].strip()

        assert dset_id_txt.startswith("ID:")
        assert dset_valid_txt.startswith("Is valid:")
        assert dset_desc_txt.startswith("Description:")
        assert dset_location_txt.startswith("Location:")

        assert dset_id == dset_id_url
        assert dset_id.isdigit()

        assert dset_name == dsets[i].name
        assert dset_id == str(dsets[i].id)
        assert dset_url.endswith(f"/datasets/ui/display/{dset_id}")
        assert dset_valid == str(dsets[i].is_valid)
        assert dset_desc == str(dsets[i].description)
        assert dset_created_dt == dsets[i].created_at
        assert dset_location == dsets[i].location

        if dsets[i].is_valid:
            assert "invalid-card" not in dataset_cards[i].get_attribute("class")
        else:
            assert "invalid-card" in dataset_cards[i].get_attribute("class")

        if dsets[i].state == "OPERATION":
            assert dset_state == "OPERATIONAL"
        else:
            assert dset_state == dsets[i].state

    assert page.get_text(page.REG_DSET_BTN) == "Register a New Dataset"
    assert page.get_text(page.IMPORT_DSET_BTN) == "Import Dataset"
    assert page.get_text(page.HEADER) == "Datasets"
    assert page.get_text(page.MINE_LABEL) == "Show only my datasets"
    assert page.find(page.MINE_SWITCH).get_attribute("data-entity-name") == "datasets"

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.is_mine()

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.not_mine()
