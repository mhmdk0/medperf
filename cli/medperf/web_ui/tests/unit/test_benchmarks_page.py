import pytest
from medperf.web_ui.tests import config as tests_config
from medperf.web_ui.tests.pages.benchmark.ui_page import BenchmarksPage
from medperf.tests.mocks.benchmark import TestBenchmark
import datetime
import selenium.common.exceptions as selenium_exceptions

BASE_URL = tests_config.BASE_URL
PATCH_GET_ALL_BMKS = "medperf.entities.benchmark.Benchmark.all"
PATCH_GET_USER_ID = "medperf.web_ui.benchmarks.routes.get_medperf_user_data"


def test_empty_benchmarks_ui_page_content(mocker, driver):
    mocker.patch(PATCH_GET_USER_ID, return_value={"id": 1})
    bmks_patch = mocker.patch(PATCH_GET_ALL_BMKS, return_value=[])
    filters = {"owner": 1}

    page = BenchmarksPage(driver)
    page.open(BASE_URL.format("/benchmarks/ui"))

    bmks_patch.assert_called_with(filters={})
    assert page.get_text(page.REG_BMK_BTN) == "Register a New Benchmark"
    assert page.get_text(page.HEADER) == "Benchmarks"
    assert page.get_text(page.MINE_LABEL) == "Show only my benchmarks"
    assert page.get_text(page.NO_BENCHMARKS) == "No benchmarks yet"
    assert page.find(page.MINE_SWITCH).get_attribute("data-entity-name") == "benchmarks"

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.is_mine()
    bmks_patch.assert_called_with(filters=filters)

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.not_mine()
    bmks_patch.assert_called_with(filters={})


def test_benchmarks_ui_page_content(mocker, driver):
    bmk1 = TestBenchmark(id=1, owner=1, created_at=datetime.datetime(2025, 1, 1))
    bmk2 = TestBenchmark(id=2, owner=2, created_at=datetime.datetime(2025, 5, 20))
    bmk1.docs_url = "https://test.test/bmk_doc"
    bmk1.description = "benchmark sample"
    bmks = [bmk1, bmk2]

    mocker.patch(PATCH_GET_USER_ID, return_value={"id": 1})
    mocker.patch(PATCH_GET_ALL_BMKS, return_value=bmks)

    page = BenchmarksPage(driver)
    page.open(BASE_URL.format("/benchmarks/ui"))

    with pytest.raises(selenium_exceptions.NoSuchElementException):
        page.driver.find_element(*page.NO_BENCHMARKS)

    benchmarks_cards = page.find_elements(page.CARDS_CONTAINER)

    assert len(benchmarks_cards) == len(bmks)

    for i in range(len(bmks)):
        bmk_name = benchmarks_cards[i].find_element(*page.CARD_TITLE).text
        bmk_url = (
            benchmarks_cards[i].find_element(*page.CARD_TITLE).get_attribute("href")
        )
        bmk_id_txt = benchmarks_cards[i].find_element(*page.CARD_ID).text
        bmk_state = benchmarks_cards[i].find_element(*page.CARD_STATE).text
        bmk_valid_txt = benchmarks_cards[i].find_element(*page.CARD_VALID).text
        bmk_desc_txt = benchmarks_cards[i].find_element(*page.CARD_DESC).text
        bmk_docs_txt = benchmarks_cards[i].find_element(*page.CARD_DOCS).text
        bmk_docs_url = (
            benchmarks_cards[i].find_element(*page.CARD_DOCS).get_attribute("href")
        )
        bmk_created = (
            benchmarks_cards[i]
            .find_element(*page.CARD_CREATED)
            .get_attribute("data-date")
        )
        bmk_approval_st_txt = benchmarks_cards[i].find_element(*page.APPROVAL).text

        bmk_id = bmk_id_txt.split(":")[-1].strip()
        bmk_id_url = bmk_url.split("/")[-1].strip()
        bmk_valid = bmk_valid_txt.split(":")[-1].strip()
        bmk_desc = bmk_desc_txt.split(":", 1)[-1].strip()
        bmk_docs_txt = bmk_docs_txt.split(":", 1)[-1].strip()
        bmk_created_dt = datetime.datetime.strptime(bmk_created, "%Y-%m-%d %H:%M:%S")
        bmk_approval_st = bmk_approval_st_txt.split(":")[-1].strip()

        assert bmk_id_txt.startswith("ID:")
        assert bmk_valid_txt.startswith("Is valid:")
        assert bmk_desc_txt.startswith("Description:")

        assert bmk_id == bmk_id_url
        assert bmk_id.isdigit()

        assert bmk_name == bmks[i].name
        assert bmk_id == str(bmks[i].id)
        assert bmk_url.endswith(f"/benchmarks/ui/display/{bmk_id}")
        assert bmk_valid == str(bmks[i].is_valid)
        assert bmk_desc == str(bmks[i].description)
        assert bmk_created_dt == bmks[i].created_at
        assert bmk_approval_st == str(bmks[i].approval_status)

        if bmks[i].is_valid:
            assert "invalid-card" not in benchmarks_cards[i].get_attribute("class")
        else:
            assert "invalid-card" in benchmarks_cards[i].get_attribute("class")

        if bmks[i].state == "OPERATION":
            assert bmk_state == "OPERATIONAL"
        else:
            assert bmk_state == bmks[i].state

        if bmk_docs_txt == "Not Available":
            assert bmks[i].docs_url is None
        else:
            assert bmk_docs_txt == "Documentation"
            assert bmk_docs_url == bmks[i].docs_url

    assert page.get_text(page.REG_BMK_BTN) == "Register a New Benchmark"
    assert page.get_text(page.HEADER) == "Benchmarks"
    assert page.get_text(page.MINE_LABEL) == "Show only my benchmarks"
    assert page.find(page.MINE_SWITCH).get_attribute("data-entity-name") == "benchmarks"

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.is_mine()

    old_url = page.current_url
    page.toggle_mine()
    page.wait_for_url_change(old_url)

    assert page.not_mine()
