from selenium.webdriver.common.by import By
from ..base_page import BasePage


class RegBenchmarkPage(BasePage):
    REG_BMK_BTN = (By.CSS_SELECTOR, '[data-testid="reg-bmk-btn"]')
    HEADER = (By.CSS_SELECTOR, 'h1[data-testid="page-header"]')
    FORM = (By.ID, "benchmark-register-form")
    NAME_LABEL = (By.CSS_SELECTOR, 'label[for="name"]')
    NAME = (By.ID, "name")
    NAME_TOOLTIP = (By.CSS_SELECTOR, '#name + i[data-bs-toggle="tooltip"]')
    DESCRIPTION_LABEL = (By.CSS_SELECTOR, 'label[for="description"]')
    DESCRIPTION = (By.ID, "description")
    DESCRIPTION_TOOLTIP = (
        By.CSS_SELECTOR,
        '#description + i[data-bs-toggle="tooltip"]',
    )
    REF_DATASET_LABEL = (By.CSS_SELECTOR, 'label[for="reference-dataset-tarball-url"]')
    REF_DATASET = (By.ID, "reference-dataset-tarball-url")
    REF_DATASET_TOOLTIP = (
        By.CSS_SELECTOR,
        '#reference-dataset-tarball-url + i[data-bs-toggle="tooltip"]',
    )
    ALREADY_PREPARED_LABEL = (By.CSS_SELECTOR, 'label[for="skip-dataprep"]')
    ALREADY_PREPARED = (By.ID, "skip-dataprep")
    NOT_PREPARED_LABEL = (By.CSS_SELECTOR, 'label[for="noskip-dataprep"]')
    NOT_PREPARED = (By.ID, "noskip-dataprep")
    DATA_PREP_LABEL = (By.CSS_SELECTOR, 'label[for="data-preparation-container"]')
    DATA_PREP = (By.ID, "data-preparation-container")
    REF_MODEL_LABEL = (By.CSS_SELECTOR, 'label[for="reference-model-container"]')
    REF_MODEL = (By.ID, "reference-model-container")
    METRICS_LABEL = (By.CSS_SELECTOR, 'label[for="evaluator-container"]')
    METRICS = (By.ID, "evaluator-container")
    REGISTER = (By.ID, "register-benchmark-btn")

    TOOLTIP = (By.CSS_SELECTOR, 'div.tooltip[role="tooltip"]')
    RESUME_SCRIPT = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-benchmark-registration"]',
    )

    def register_benchmark(
        self,
        name,
        description,
        reference_dataset,
        data_preparator,
        reference_model,
        metrics,
    ):
        self.type(self.NAME, name)
        self.type(self.DESCRIPTION, description)
        self.type(self.REF_DATASET, reference_dataset)

        self.select_by_text(self.DATA_PREP, data_preparator)
        self.select_by_text(self.REF_MODEL, reference_model)
        self.select_by_text(self.METRICS, metrics)

        self.click(self.REGISTER)
