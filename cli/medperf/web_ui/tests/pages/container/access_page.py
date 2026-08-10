from selenium.webdriver.common.by import By

from ..base_page import BasePage


class ContainerAccessPage(BasePage):
    BACK_LINK = (By.CSS_SELECTOR, "a[href^='/containers/ui/display/']")
    HEADER = (By.CSS_SELECTOR, "h1")

    GRANT_FORM = (By.ID, "grant-access-form")
    BENCHMARK = (By.ID, "benchmark")
    EMAIL_INPUT = (By.ID, "email-input")
    GRANT_BTN = (By.ID, "grant-access-btn")

    BENCHMARK_AUTO = (By.ID, "benchmark-auto")
    INTERVAL_AUTO = (By.ID, "interval-auto")
    EMAIL_INPUT_AUTO = (By.ID, "email-input-auto")
    START_AUTO_BTN = (By.ID, "start-auto-access-btn")
    STOP_AUTO_BTN = (By.ID, "stop-auto-access-btn")
    RUNNING_BADGE = (By.ID, "running-badge")

    NO_KEYS_MSG = (By.XPATH, "//p[contains(., 'No users currently have access')]")
    KEYS_TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")

    DELETE_KEYS_FORM = (By.ID, "delete-keys-form")
    DELETE_KEYS_BTN = (By.ID, "delete-keys-btn")

    def revoke_btn(self, key_id):
        return (By.ID, f"revoke-btn-{key_id}")

    def grant_access(self, benchmark, emails):
        self.select_searchable_entity(self.BENCHMARK, benchmark)
        self.type(self.EMAIL_INPUT, ",".join(emails) + ",")
        self.click(self.GRANT_BTN)

    def revoke_access(self, key_id):
        self.click(self.revoke_btn(key_id))

    def delete_keys(self):
        self.click(self.DELETE_KEYS_BTN)

    def start_auto_access(self, benchmark, emails):
        self.select_searchable_entity(self.BENCHMARK_AUTO, benchmark)
        self.type(self.EMAIL_INPUT_AUTO, ",".join(emails) + ",")
        self.click(self.START_AUTO_BTN)

    def stop_auto_access(self):
        self.click(self.STOP_AUTO_BTN)
