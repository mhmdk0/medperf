from medperf.web_ui.tests import config as tests_config
from medperf.web_ui.tests.pages.security_page import SecurityPage

BASE_URL = tests_config.BASE_URL


def test_security_page_content(driver_noauth):
    page = SecurityPage(driver_noauth)
    page.open(BASE_URL.format("/"))

    assert "/security_check" in page.current_url

    page.wait_for_presence_selector(page.FORM)

    assert page.get_text(page.HEADER) == "Security Check"
    assert (
        page.get_text(page.TOKEN_LABEL)
        == "Enter your Security Token printed in MedPerf CLI output"
    )
    assert page.get_text(page.HELP_BTN) == "Why is this required?"

    help_modal = page.find(page.HELP_MODAL)

    assert help_modal.is_displayed() is False

    page.click(page.HELP_BTN)
    page.wait_for_visibility_element(help_modal)
    help_modal.find_element(*page.CLOSE_HELP).click()


def test_security_check_page_wrong_token(driver_noauth):
    page = SecurityPage(driver_noauth)
    page.open(BASE_URL.format("/"))
    page.enter_token("wrong_token")
    page.wait_for_presence_selector(page.ERROR)

    assert page.get_text(page.ERROR) == "Invalid token"


def test_security_check_page_correct_token(driver_noauth, sec_token):
    page = SecurityPage(driver_noauth)
    page.open(BASE_URL.format("/"))
    old_url = page.current_url
    page.enter_token(sec_token)
    page.wait_for_url_change(old_url)

    assert "/benchmarks/ui" in page.current_url
