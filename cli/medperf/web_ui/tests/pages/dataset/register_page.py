from selenium.webdriver.common.by import By
from ..base_page import BasePage


class RegDatasetPage(BasePage):
    REG_DSET_BTN = (By.CSS_SELECTOR, '[data-testid="reg-dset-btn"]')
    HEADER = (By.CSS_SELECTOR, 'h1[data-testid="page-header"]')
    FORM = (By.ID, "dataset-register-form")
    BENCHMARK_LABEL = (By.CSS_SELECTOR, 'label[for="benchmark"]')
    BENCHMARK = (By.ID, "benchmark")
    NAME_LABEL = (By.CSS_SELECTOR, 'label[for="name"]')
    NAME = (By.ID, "name")
    NAME_TOOLTIP = (By.CSS_SELECTOR, '#name + i[data-bs-toggle="tooltip"]')
    DESCRIPTION_LABEL = (By.CSS_SELECTOR, 'label[for="description"]')
    DESCRIPTION = (By.ID, "description")
    DESCRIPTION_TOOLTIP = (
        By.CSS_SELECTOR,
        '#description + i[data-bs-toggle="tooltip"]',
    )
    LOCATION_LABEL = (By.CSS_SELECTOR, 'label[for="location"]')
    LOCATION = (By.ID, "location")
    LOCATION_TOOLTIP = (By.CSS_SELECTOR, '#location + i[data-bs-toggle="tooltip"]')
    DATA_LABEL = (By.CSS_SELECTOR, 'label[for="data-path"]')
    DATA = (By.ID, "data-path")
    DATA_BROWSE = (By.ID, "browse-data-btn")
    DATA_TOOLTIP = (By.CSS_SELECTOR, '#data-path ~ i[data-bs-toggle="tooltip"]')
    LABELS_LABEL = (By.CSS_SELECTOR, 'label[for="labels-path"]')
    LABELS = (By.ID, "labels-path")
    LABELS_BROWSE = (By.ID, "browse-labels-btn")
    LABELS_TOOLTIP = (By.CSS_SELECTOR, '#labels-path ~ i[data-bs-toggle="tooltip"]')
    REGISTER = (By.ID, "register-dataset-btn")

    PICKER_MODAL = (By.ID, "folder-picker-modal")
    PICKER_PATH = (By.CSS_SELECTOR, "#folder-picker-modal-title code")
    PICKER_FOLDERS = (By.CSS_SELECTOR, "#folder-list li")
    PICKER_SELECT = (By.ID, "select-folder-btn")
    PICKER_CANCEL = (
        By.CSS_SELECTOR,
        '#folder-picker-modal button[data-bs-dismiss="modal"]',
    )

    TOOLTIP = (By.CSS_SELECTOR, 'div.tooltip[role="tooltip"]')
    RESUME_SCRIPT = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-dataset-registration"]',
    )

    def register_dataset(
        self,
        benchmark,
        name,
        description,
        location,
        data_path,
        labels_path,
    ):
        self.select_by_text(self.BENCHMARK, benchmark)

        self.type(self.NAME, name)
        self.type(self.DESCRIPTION, description)
        self.type(self.LOCATION, location)
        self.type(self.DATA, data_path)
        self.type(self.LABELS, labels_path)

        self.click(self.REGISTER)
