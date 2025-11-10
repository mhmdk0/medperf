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
    DOCUMENTATION = (By.CSS_SELECTOR, 'a[data-testid="documentation"]')
    NO_DOCUMENTATION = (By.CSS_SELECTOR, 'span[data-testid="documentation"]')

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

    DATASET_AUTO_APPROVE_LABEL = (
        By.CSS_SELECTOR,
        'label[for="dataset-auto-approve-mode"]',
    )
    DATASET_AUTO_APPROVE = (By.ID, "dataset-auto-approve-mode")
    DATASET_ALLOW_LIST_CONTAINER = (By.ID, "dataset-allow-list-container")
    DATASET_ALLOW_LIST_EMAILS = (By.ID, "dataset-allow-list-emails")
    DATASET_ALLOW_LIST_LABEL = (
        By.CSS_SELECTOR,
        'label[for="dataset-allow-list-text-input"]',
    )
    DATASET_ALLOW_LIST = (By.ID, "dataset-allow-list-text-input")

    MODEL_AUTO_APPROVE_LABEL = (
        By.CSS_SELECTOR,
        'label[for="model-auto-approve-mode"]',
    )
    MODEL_AUTO_APPROVE = (By.ID, "model-auto-approve-mode")
    MODEL_ALLOW_LIST_CONTAINER = (By.ID, "model-allow-list-container")
    MODEL_ALLOW_LIST_EMAILS = (By.ID, "model-allow-list-emails")
    MODEL_ALLOW_LIST_LABEL = (
        By.CSS_SELECTOR,
        'label[for="model-allow-list-text-input"]',
    )
    MODEL_ALLOW_LIST = (By.ID, "model-allow-list-text-input")

    EMAIL_CHIP = (By.CSS_SELECTOR, ".email-chip")
    REMOVE_EMAIL = (By.CSS_SELECTOR, ".remove-btn")
    SAVE = (By.ID, "save-policy-btn")

    ASSOCIATIONS_RESULTS_CONTAINER = (
        By.CSS_SELECTOR,
        'div[data-testid="associations-results"]',
    )

    DATASETS_TITLE = (By.ID, "datasets-associations-title")
    DATASETS_ASSOCIATIONS = (By.ID, "datasets-associations")
    DATASETS_ASSOCIATIONS_CARDS = (By.CSS_SELECTOR, "#datasets-associations > div.card")
    DATASETS_ASSOCS_COUNT = (
        By.CSS_SELECTOR,
        '#datasets-associations-title span[data-testid="associations-count"].badge',
    )
    DATASETS_PENDING_ASSOCS = (
        By.CSS_SELECTOR,
        '#datasets-associations-title span[data-testid="pending-associations"].fst-italic',
    )

    MODELS_TITLE = (By.ID, "models-associations-title")
    MODELS_ASSOCIATIONS = (By.ID, "models-associations")
    MODELS_ASSOCIATIONS_CARDS = (By.CSS_SELECTOR, "#models-associations > div.card")
    MODELS_ASSOCS_COUNT = (
        By.CSS_SELECTOR,
        '#models-associations-title span[data-testid="associations-count"].badge',
    )
    MODELS_PENDING_ASSOCS = (
        By.CSS_SELECTOR,
        '#models-associations-title span[data-testid="pending-associations"].fst-italic',
    )

    RESULTS_TITLE = (By.ID, "benchmark-results-title")
    RESULTS = (By.ID, "benchmark-results")
    RESULTS_CARDS = (By.CSS_SELECTOR, "#benchmark-results > div.card")
    RESULTS_COUNT = (
        By.CSS_SELECTOR,
        '#benchmark-results-title span[data-testid="associations-count"].badge',
    )

    RESULT_MODAL = (By.ID, "result-modal")
    CLOSE_BTN = (By.CSS_SELECTOR, 'button[data-bs-dismiss="modal"][aria-label="Close"]')

    RESULT_BTN = (By.CLASS_NAME, "view-result-btn")

    CONFIRM_TEXT = (By.ID, "confirm-text")

    ASSOC_NAME = (By.CSS_SELECTOR, 'h5[data-testid="assoc-entity-name"]')
    ASSOC_ANCHOR = (By.CSS_SELECTOR, 'a[data-testid="assoc-entity-anchor"]')
    ASSOC_APPROVAL_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="assoc-approval-status-label"]',
    )
    ASSOC_APPROVAL = (By.CSS_SELECTOR, 'span[data-testid="assoc-approval-status"]')
    ASSOC_REJECT = (By.CSS_SELECTOR, 'button[data-testid="assoc-reject-btn"]')
    ASSOC_APPROVE = (By.CSS_SELECTOR, 'button[data-testid="assoc-approve-btn"]')
    ASSOC_APPROVED_AT_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="assoc-approved-at-label"]',
    )
    ASSOC_APPROVED_AT = (By.CSS_SELECTOR, 'span[data-testid="assoc-approved-at"]')
    ASSOC_MODIFIED_AT_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="assoc-modified-label"]',
    )
    ASSOC_MODIFIED_AT = (By.CSS_SELECTOR, 'span[data-testid="assoc-modified"]')
    ASSOC_INITIATED_BY_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="assoc-initiated-by-label"]',
    )
    ASSOC_INITIATED_BY = (By.CSS_SELECTOR, 'span[data-testid="assoc-initiated-by"]')

    RESULT_NAME = (By.CSS_SELECTOR, 'h5[data-testid="result-name"]')
    RESULT_VIEW = (By.CSS_SELECTOR, 'button[data-testid="view-btn"]')
    RESULT_NOT_SUBMITTED = (By.CSS_SELECTOR, 'h5[data-testid="not-submitted"]')
    RESULT_OWNER_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="result-owner-label"]')
    RESULT_OWNER = (By.CSS_SELECTOR, 'span[data-testid="result-owner"]')
    RESULT_MODEL_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="result-model-label"]')
    RESULT_MODEL = (By.CSS_SELECTOR, 'a[data-testid="result-model"]')
    RESULT_DATASET_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="result-dataset-label"]',
    )
    RESULT_DATASET = (By.CSS_SELECTOR, 'a[data-testid="result-dataset"]')
    RESULT_INFERENCE_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="result-inference-label"]',
    )
    RESULT_INFERENCE = (By.CSS_SELECTOR, 'span[data-testid="result-inference"]')
    RESULT_METRICS_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="result-metrics-label"]',
    )
    RESULT_METRICS = (By.CSS_SELECTOR, 'span[data-testid="result-metrics"]')
    RESULT_MODIFIED_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="result-modified-label"]',
    )
    RESULT_MODIFIED = (By.CSS_SELECTOR, 'span[data-testid="result-modified"]')

    def __init__(self, driver, benchmark="", entity_name=""):
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
