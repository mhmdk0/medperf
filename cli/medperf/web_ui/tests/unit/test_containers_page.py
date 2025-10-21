import pytest
from medperf.web_ui.tests import config as tests_config
from medperf.web_ui.tests.pages.container.ui_page import ContainersPage
from medperf.tests.mocks.cube import TestCube
import datetime
import selenium.common.exceptions as selenium_exceptions

BASE_URL = tests_config.BASE_URL
PATCH_GET_ALL_CONTS = "medperf.entities.cube.Cube.all"
PATCH_GET_USER_ID = "medperf.web_ui.containers.routes.get_medperf_user_data"


def test_empty_containers_ui_page_content(mocker, driver):
    mocker.patch(PATCH_GET_USER_ID, return_value={"id": 1})
    conts_patch = mocker.patch(PATCH_GET_ALL_CONTS, return_value=[])
    filters = {"owner": 1}

    page = ContainersPage(driver)
    page.open(BASE_URL.format("/containers/ui"))

    conts_patch.assert_called_with(filters={})
    assert page.get_text(page.REG_DSET_BTN) == "Register a New Container"
    assert page.get_text(page.HEADER) == "Containers"
    assert page.get_text(page.MINE_LABEL) == "Show only my containers"
    assert page.get_text(page.NO_CONTAINERS) == "No containers yet"
    assert page.find(page.MINE_SWITCH).get_attribute("data-entity-name") == "containers"

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.is_mine()
    conts_patch.assert_called_with(filters=filters)

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.not_mine()
    conts_patch.assert_called_with(filters={})


def test_containers_ui_page_content(mocker, driver):
    cont1 = TestCube(id=1, owner=1, created_at=datetime.datetime(2025, 1, 1))
    cont2 = TestCube(id=2, owner=2, created_at=datetime.datetime(2025, 5, 20))
    conts = [cont1, cont2]

    mocker.patch(PATCH_GET_USER_ID, return_value={"id": 1})
    mocker.patch(PATCH_GET_ALL_CONTS, return_value=conts)

    page = ContainersPage(driver)
    page.open(BASE_URL.format("/containers/ui"))

    with pytest.raises(selenium_exceptions.NoSuchElementException):
        page.driver.find_element(*page.NO_CONTAINERS)

    containers_cards = page.find_elements(page.CARDS_CONTAINER)

    assert len(containers_cards) == len(conts)

    for i in range(len(conts)):
        cont_name = containers_cards[i].find_element(*page.CARD_TITLE).text
        cont_url = (
            containers_cards[i].find_element(*page.CARD_TITLE).get_attribute("href")
        )
        cont_id_txt = containers_cards[i].find_element(*page.CARD_ID).text
        cont_state = containers_cards[i].find_element(*page.CARD_STATE).text
        cont_valid_txt = containers_cards[i].find_element(*page.CARD_VALID).text
        cont_created = (
            containers_cards[i]
            .find_element(*page.CARD_CREATED)
            .get_attribute("data-date")
        )

        cont_id = cont_id_txt.split(":")[-1].strip()
        cont_id_url = cont_url.split("/")[-1].strip()
        cont_valid = cont_valid_txt.split(":")[-1].strip()
        cont_created_dt = datetime.datetime.strptime(cont_created, "%Y-%m-%d %H:%M:%S")

        assert cont_id_txt.startswith("ID:")
        assert cont_valid_txt.startswith("Is valid:")

        assert cont_id == cont_id_url
        assert cont_id.isdigit()

        assert cont_name == conts[i].name
        assert cont_id == str(conts[i].id)
        assert cont_url.endswith(f"/containers/ui/display/{cont_id}")
        assert cont_valid == str(conts[i].is_valid)
        assert cont_created_dt == conts[i].created_at

        if conts[i].is_valid:
            assert "invalid-card" not in containers_cards[i].get_attribute("class")
        else:
            assert "invalid-card" in containers_cards[i].get_attribute("class")

        if conts[i].state == "OPERATION":
            assert cont_state == "OPERATIONAL"
        else:
            assert cont_state == conts[i].state

    assert page.get_text(page.REG_DSET_BTN) == "Register a New Container"
    assert page.get_text(page.HEADER) == "Containers"
    assert page.get_text(page.MINE_LABEL) == "Show only my containers"
    assert page.find(page.MINE_SWITCH).get_attribute("data-entity-name") == "containers"

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.is_mine()

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.not_mine()
