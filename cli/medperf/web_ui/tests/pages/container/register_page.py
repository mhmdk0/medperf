from selenium.webdriver.common.by import By
from ..base_page import BasePage


class RegContainerPage(BasePage):
    REG_CONTAINER_BTN = (By.CSS_SELECTOR, '[data-testid="reg-cont-btn"]')
    HEADER = (By.CSS_SELECTOR, 'h1[data-testid="page-header"]')
    FORM = (By.ID, "container-register-form")
    NAME_LABEL = (By.CSS_SELECTOR, 'label[for="name"]')
    NAME = (By.ID, "name")
    NAME_TOOLTIP = (By.CSS_SELECTOR, '#name + i[data-bs-toggle="tooltip"]')
    MANIFEST_LABEL = (By.CSS_SELECTOR, 'label[for="container-file"]')
    MANIFEST = (By.ID, "container-file")
    MANIFEST_TOOLTIP = (
        By.CSS_SELECTOR,
        '#container-file + i[data-bs-toggle="tooltip"]',
    )
    PARAMETERS_LABEL = (By.CSS_SELECTOR, 'label[for="parameters-file"]')
    PARAMETERS = (By.ID, "parameters-file")
    PARAMETERS_TOOLTIP = (
        By.CSS_SELECTOR,
        '#parameters-file + i[data-bs-toggle="tooltip"]',
    )
    ADDITIONAL_LABEL = (By.CSS_SELECTOR, 'label[for="additional-file"]')
    ADDITIONAL = (By.ID, "additional-file")
    ADDITIONAL_TOOLTIP = (
        By.CSS_SELECTOR,
        '#additional-file + i[data-bs-toggle="tooltip"]',
    )
    REGISTER = (By.ID, "register-container-btn")

    TOOLTIP = (By.CSS_SELECTOR, 'div.tooltip[role="tooltip"]')
    RESUME_SCRIPT = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-container-registration"]',
    )

    def register_container(self, container_dict):
        self.type(self.NAME, container_dict["name"])
        self.type(self.MANIFEST, container_dict["manifest"])
        if container_dict["parameters"]:
            self.type(self.PARAMETERS, container_dict["parameters"])
        if container_dict["additional"]:
            self.type(self.ADDITIONAL, container_dict["additional"])

        self.click(self.REGISTER)
