from selenium.webdriver.common.by import By
from ..base_page import BasePage


class DatasetDetailsPage(BasePage):
    HEADER = (By.CSS_SELECTOR, 'h1[data-testid="page-header"]')
    EXPORT_FORM = (By.CSS_SELECTOR, 'form[data-testid="export-form"]')
    EXPORT = (By.CSS_SELECTOR, "#redirect-export-form input[name='submit']")
    SUB_HEADER_1 = (By.CSS_SELECTOR, 'h5[data-testid="sub-header-1"]')

    STATE = (By.CSS_SELECTOR, 'span[data-testid="dataset-state"].badge')
    VALID = (By.CSS_SELECTOR, 'span[data-testid="dataset-is-valid"].badge')

    ID_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="id-label"]')
    ID = (By.CSS_SELECTOR, 'span[data-testid="id"]')

    DESCRIPTION_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="description-label"]')
    DESCRIPTION = (By.CSS_SELECTOR, 'span[data-testid="description"]')

    LOCATION_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="location-label"]')
    LOCATION = (By.CSS_SELECTOR, 'span[data-testid="location"]')

    DATA_PREP_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="data-prep-label"]')
    DATA_PREP = (By.CSS_SELECTOR, 'span[data-testid="data-prep"] > strong > a')
    DATA_PREP_DATE = (By.CSS_SELECTOR, 'span[data-testid="data-prep"] > small')
    DATA_PREP_STATE = (By.CSS_SELECTOR, 'span[data-testid="data-prep"] > span > i')

    STATISTICS_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="statistics-label"]')
    STATISTICS = (By.CSS_SELECTOR, 'a[data-testid="statistics"]')

    REPORT_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="report-label"]')
    REPORT = (By.CSS_SELECTOR, 'a[data-testid="report"]')

    PREPARED_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="prepared-label"]')
    PREPARED = (By.CSS_SELECTOR, 'span[data-testid="prepared"]')

    OWNER_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="owner-label"]')
    OWNER = (By.CSS_SELECTOR, 'span[data-testid="owner"]')

    CREATED_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="created-at-label"]')
    CREATED = (By.CSS_SELECTOR, 'span[data-testid="created-at"]')

    MODIFIED_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="modified-at-label"]')
    MODIFIED = (By.CSS_SELECTOR, 'span[data-testid="modified-at"]')

    BOTTOM_BUTTONS_CONTAINER = (
        By.CSS_SELECTOR,
        'div[data-testid="bottom-buttons-panel"]',
    )

    PREPARED_TEXT = (
        By.CSS_SELECTOR,
        'span.text-success[data-testid="dataset-prepared"]',
    )
    PREPARE_BTN = (By.ID, "prepare-dataset")
    PERPARE_NOTE = (By.CSS_SELECTOR, 'small[data-testid="prepare-note"')

    SET_OPERATIONAL_TEXT = (
        By.CSS_SELECTOR,
        'span.text-success[data-testid="dataset-operational"]',
    )
    SET_OPERATIONAL_BTN = (By.ID, "set-operational")
    DISABLED_SET_OPERATIONAL = (
        By.CSS_SELECTOR,
        'button[data-testid="disabled-set-operational"]',
    )
    SET_OPERATIONAL_NOTE = (
        By.CSS_SELECTOR,
        'small[data-testid="set-operational-note"]',
    )

    DROPDOWN_BTN = (By.ID, "associate-dropdown-btn")
    DROPDOWN_CONTAINER = (By.ID, "dropdown-div")
    BMK_DATA = (By.CSS_SELECTOR, 'strong[data-testid="bmk-data"]')
    BMK_VIEW = (By.CSS_SELECTOR, 'a[data-testid="bmk-view"]')
    BMK_ASSOCIATE = (By.CSS_SELECTOR, 'button[data-testid="bmk-associate"]')
    NO_BMKS = (By.CSS_SELECTOR, 'li[data-testid="no-bmks"]')
    DISABLED_ASSOCIATE = (By.CSS_SELECTOR, 'button[data-testid="disabled-associate"]')
    ASSCOATE_NOTE = (By.CSS_SELECTOR, 'small[data-testid="associate-note"]')

    ASSOCIATIONS_CONTAINER = (
        By.CSS_SELECTOR,
        'div[data-testid="associations-container"]',
    )
    ASSOCIATIONS_TITLE = (
        By.CSS_SELECTOR,
        'h4[data-testid="associations-container-title"]',
    )

    BMKS_ASSOCIATIONS = (By.CSS_SELECTOR, 'li[data-testid="assoc-card"]')
    ASSOC_LABEL = (By.CSS_SELECTOR, 'span[data-testid="assoc-benchmark-label"]')
    ASSOC_BMK = (By.CSS_SELECTOR, 'a[data-testid="assoc-benchmark"]')
    ASSOC_STATUS_LABEL = (By.CSS_SELECTOR, 'span[data-testid="assoc-status-label"]')
    ASSOC_STATUS = (By.CSS_SELECTOR, 'strong[data-testid="assoc-status"]')

    APPROVED_BMKS = (By.CSS_SELECTOR, 'div[data-testid="approved-bmk"]')
    BMK_LABEL = (By.CSS_SELECTOR, 'span[data-testid="bmk-title"]')
    BMK_NAME = (By.CSS_SELECTOR, 'a[data-testid="bmk-name"]')
    BMK_RUN_ALL = (By.CSS_SELECTOR, 'button[data-testid="run-all-btn"]')

    REF_MODEL_CARD = (By.CSS_SELECTOR, 'li[data-testid="ref-model-card"]')
    REF_MODEL_LABEL = (By.CSS_SELECTOR, 'small[data-testid="ref-model-label"]')
    REF_MODEL = (By.CSS_SELECTOR, 'span[data-testid="ref-model"] > strong > a')
    REF_MODEL_DATE = (By.CSS_SELECTOR, 'span[data-testid="ref-model"] > small')
    REF_MODEL_STATE = (By.CSS_SELECTOR, 'span[data-testid="ref-model"] > span > i')

    MODEL_CARD = (By.CSS_SELECTOR, 'li[data-testid="model-card"]')
    MODEL_LABEL = (By.CSS_SELECTOR, 'small[data-testid="model-label"]')
    MODEL = (By.CSS_SELECTOR, 'span[data-testid="model"] > strong > a')
    MODEL_DATE = (By.CSS_SELECTOR, 'span[data-testid="model"] > small')
    MODEL_STATE = (By.CSS_SELECTOR, 'span[data-testid="model"] > span > i')

    RUN_MODEL_BTN = (By.CSS_SELECTOR, 'button[data-testid="run-model"]')
    VIEW_RESULT_BTN = (By.CSS_SELECTOR, 'button[data-testid="view-result"]')
    SUBMITTED_TEXT = (By.CSS_SELECTOR, 'span[data-testid="result-submitted"]')
    SUBMIT_BTN = (By.CSS_SELECTOR, 'button[data-testid="result-submit"]')

    ASSOCIATION_CARDS = (By.CSS_SELECTOR, "div.benchmark-section li a")

    RESULT_MODAL = (By.ID, "result-modal")
    CLOSE_BTN = (By.CSS_SELECTOR, 'button[data-bs-dismiss="modal"][aria-label="Close"]')

    RESUME_SCRIPT_PREPARE = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-dataset-preparation"]',
    )

    RESUME_SCRIPT_SET_OPERATIONAL = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-dataset-set-operational"]',
    )

    RESUME_SCRIPT_ASSOCIATE = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-dataset-association"]',
    )

    RESUME_SCRIPT_RUN_EXECUTION = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-dataset-execution"]',
    )

    RESUME_SCRIPT_SUBMIT_RESULT = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-dataset-result-submission"]',
    )

    CONFIRM_TEXT = (By.ID, "confirm-text")

    def __init__(self, driver, dataset="", benchmark=""):
        super().__init__(driver)
        self.DATASET_NAME_BTN = (
            By.XPATH,
            f'//h5//a[@data-testid="dset-name" and contains(text(), "{dataset}")]',
        )
        self.RUN_BTN = (
            By.XPATH,
            f'//div[contains(@class,"card")][.//h4//a/strong[text()="{benchmark}"]]'
            + '//button[contains(@class,"run-all-btn")]',
        )
        self.VIEW_BTNS = (
            By.XPATH,
            f'//div[contains(@class,"card")][.//h4//a/strong[text()="{benchmark}"]]//button[contains(text(),"View Result")]',
        )
        self.SUBMIT_BTNS = (
            By.XPATH,
            f'//div[contains(@class,"card")][.//h4//a/strong[text()="{benchmark}"]]//button[contains(text(),"Submit")]',
        )

        self.ASSOCIATE_BTN = (
            By.XPATH,
            f'//li[.//strong[contains(text(), "{benchmark}")]]//button[contains(@class, "request-association-btn")]',
        )

    def prepare_dataset(self):
        self.click(self.PREPARE_BTN)

    def set_operational(self):
        self.click(self.SET_OPERATIONAL_BTN)

    def request_association(self):
        self.click(self.DROPDOWN_BTN)
        self.click(self.ASSOCIATE_BTN)

    def get_association_cards_titles(self):
        return [i.text for i in self.driver.find_elements(*self.ASSOCIATION_CARDS)]

    def run_execution(self):
        self.click(self.RUN_BTN)

    def __view_result(self, view_btn):
        self.ensure_element_ready(view_btn)
        view_btn.click()
        view_modal = self.find(self.RESULT_MODAL)
        self.wait_for_visibility_element(view_modal)
        view_modal.find_element(*self.CLOSE_BTN).click()

    def view_results(self):
        view_btns = self.driver.find_elements(*self.VIEW_BTNS)
        for view_btn in view_btns:
            self.__view_result(view_btn)

    def submit_result(self, submit_btn):
        self.ensure_element_ready(submit_btn)
        submit_btn.click()

    def get_submit_buttons(self):
        return self.driver.find_elements(*self.SUBMIT_BTNS)
