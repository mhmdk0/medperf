from selenium.webdriver.common.by import By
from ..base_page import BasePage


class BenchmarkDetailsPage(BasePage):
    HEADER = (By.CSS_SELECTOR, 'h1[data-testid="page-header"]')
    SUB_HEADER_1 = (By.CSS_SELECTOR, 'h5[data-testid="sub-header-1"]')

    STATE = (By.CSS_SELECTOR, 'span[data-testid="bmk-state"].badge')
    VALID = (By.CSS_SELECTOR, 'span[data-testid="bmk-is-valid"].badge')

    ID_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="id-label"]')
    ID = (By.CSS_SELECTOR, 'span[data-testid="id"]')

    DESCRIPTION_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="description-label"]')
    DESCRIPTION = (By.CSS_SELECTOR, 'span[data-testid="description"]')

    DOCUMENTATION_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="documentation-label"]')
    DOCUMENTATION = (By.CSS_SELECTOR, 'span[data-testid="documentation"]')

    REF_DATASET_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="ref-dataset-tarball-label"]',
    )
    REF_DATASET = (By.CSS_SELECTOR, 'a[data-testid="ref-dataset-tarball"]')

    DATA_PREP_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="data-prep-label"]')
    DATA_PREP = (By.CSS_SELECTOR, 'span[data-testid="data-prep"] > strong > a')
    DATA_PREP_DATE = (By.CSS_SELECTOR, 'span[data-testid="data-prep"] > small')
    DATA_PREP_STATE = (By.CSS_SELECTOR, 'span[data-testid="data-prep"] > span > i')

    REF_MODEL_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="ref-model-label"]')
    REF_MODEL = (By.CSS_SELECTOR, 'span[data-testid="ref-model"] > strong > a')
    REF_MODEL_DATE = (By.CSS_SELECTOR, 'span[data-testid="ref-model"] > small')
    REF_MODEL_STATE = (By.CSS_SELECTOR, 'span[data-testid="ref-model"] > span > i')

    METRICS_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="metrics-label"]')
    METRICS = (By.CSS_SELECTOR, 'span[data-testid="metrics"] > strong > a')
    METRICS_DATE = (By.CSS_SELECTOR, 'span[data-testid="metrics"] > small')
    METRICS_STATE = (By.CSS_SELECTOR, 'span[data-testid="metrics"] > span > i')

    OWNER_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="owner-label"]')
    OWNER = (By.CSS_SELECTOR, 'span[data-testid="owner"]')

    CREATED_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="created-at-label"]')
    CREATED = (By.CSS_SELECTOR, 'span[data-testid="created-at"]')

    MODIFIED_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="modified-at-label"]')
    MODIFIED = (By.CSS_SELECTOR, 'span[data-testid="modified-at"]')

    SUB_HEADER_2 = (By.CSS_SELECTOR, 'h5[data-testid="sub-header-2"]')
    POLICY_FORM = (By.ID, "association-policy-form")

    DSET_AUTO_APPROVE_LABEL = (
        By.CSS_SELECTOR,
        'label[for="dataset-auto-approve-mode"]',
    )
    DSET_AUTO_APPROVE = (By.ID, "dataset-auto-approve-mode")
    DSET_ALLOW_LIST_CONTAINER = (By.ID, "dataset-allow-list-container")
    DSET_ALLOW_LIST_EMAILS = (By.ID, "dataset-allow-list-emails")
    DSET_ALLOW_LIST_LABEL = (
        By.CSS_SELECTOR,
        'label[for="dataset-allow-list-text-input"]',
    )
    DSET_ALLOW_LIST = (By.ID, "dataset-allow-list-text-input")

    CONT_AUTO_APPROVE_LABEL = (
        By.CSS_SELECTOR,
        'label[for="dataset-auto-approve-mode"]',
    )
    CONT_AUTO_APPROVE = (By.ID, "dataset-auto-approve-mode")
    CONT_ALLOW_LIST_CONTAINER = (By.ID, "dataset-allow-list-container")
    CONT_ALLOW_LIST_EMAILS = (By.ID, "dataset-allow-list-emails")
    CONT_ALLOW_LIST_LABEL = (
        By.CSS_SELECTOR,
        'label[for="dataset-allow-list-text-input"]',
    )
    CONT_ALLOW_LIST = (By.ID, "dataset-allow-list-text-input")

    SAVE = (By.ID, "save-policy-btn")

    DATASETS_TITLE = (By.ID, "datasets-associations-title")
    DATASETS_ASSOCIATIONS = (By.ID, "datasets-associations")

    MODELS_TITLE = (By.ID, "models-associations-title")
    MODELS_ASSOCIATIONS = (By.ID, "models-associations")

    RESULTS_TITLE = (By.ID, "benchmark-results-title")
    RESULTS = (By.ID, "benchmark-results")

    RESULT_MODAL = (By.ID, "result-modal")
    CLOSE_BTN = (By.CSS_SELECTOR, 'button[data-bs-dismiss="modal"][aria-label="Close"]')

    RESULT_BTN = (By.CLASS_NAME, "view-result-btn")

    def __init__(self, driver, benchmark, entity_name=""):
        super().__init__(driver)
        self.BMK_BTN = (
            By.XPATH,
            f'//a[@data-testid="bmk-name" and contains(text(), "{benchmark}")]',
        )
        self.APPROVE_BTN = (
            By.XPATH,
            f'//div[contains(@class,"association-card")] [.//h5[contains(text(), "{entity_name}")]]'
            + ' //button[@data-action-name="approve"]',
        )

    def approve_dataset(self):
        self.click(self.DATASETS_TITLE)
        associations = self.find(self.DATASETS_ASSOCIATIONS)
        self.wait_for_visibility_element(associations)
        self.click(self.APPROVE_BTN)

    def approve_container(self):
        self.click(self.MODELS_TITLE)
        associations = self.find(self.MODELS_ASSOCIATIONS)
        self.wait_for_visibility_element(associations)
        self.click(self.APPROVE_BTN)

    def __view_result(self, result_btn):
        self.ensure_element_ready(result_btn)
        result_btn.click()
        view_modal = self.find(self.RESULT_MODAL)
        self.wait_for_visibility_element(view_modal)
        view_modal.find_element(*self.CLOSE_BTN).click()

    def view_results(self):
        self.click(self.RESULTS_TITLE)
        associations = self.find(self.RESULTS)
        self.wait_for_visibility_element(associations)
        for result_btn in associations.find_elements(*self.RESULT_BTN):
            self.__view_result(result_btn)
