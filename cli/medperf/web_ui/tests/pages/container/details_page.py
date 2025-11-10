from selenium.webdriver.common.by import By
from ..base_page import BasePage


class ContainerDetailsPage(BasePage):
    HEADER = (By.CSS_SELECTOR, 'h1[data-testid="page-header"]')
    SUB_HEADER_1 = (By.CSS_SELECTOR, 'h5[data-testid="sub-header-1"]')
    SUB_HEADER_2 = (By.CSS_SELECTOR, 'h2[data-testid="sub-header-2"]')

    STATE = (By.CSS_SELECTOR, 'span[data-testid="container-state"].badge')
    VALID = (By.CSS_SELECTOR, 'span[data-testid="container-is-valid"].badge')

    ID_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="id-label"]')
    ID = (By.CSS_SELECTOR, 'span[data-testid="id"]')

    MANIFEST_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="manifest-label"]')
    MANIFEST = (By.CSS_SELECTOR, 'a[data-testid="manifest"]')

    PARAMETERS_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="parameters-label"]')
    PARAMETERS = (By.CSS_SELECTOR, 'a[data-testid="parameters"]')

    TARBALL_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="tarball-label"]')
    TARBALL = (By.CSS_SELECTOR, 'a[data-testid="tarball"]')
    NO_TARBALL = (By.CSS_SELECTOR, 'span[data-testid="no-tarball"]')

    ADDITIONAL_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="additional-label"]')
    ADDITIONAL = (By.CSS_SELECTOR, 'a[data-testid="additional"]')
    NO_ADDITIONAL = (By.CSS_SELECTOR, 'span[data-testid="no-additional"]')

    OWNER_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="owner-label"]')
    OWNER = (By.CSS_SELECTOR, 'span[data-testid="owner"]')

    CREATED_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="created-label"]')
    CREATED = (By.CSS_SELECTOR, 'span[data-testid="created"]')

    MODIFIED_LABEL = (By.CSS_SELECTOR, 'strong[data-testid="modified-label"]')
    MODIFIED = (By.CSS_SELECTOR, 'span[data-testid="modified"]')

    BOTTOM_BUTTONS_CONTAINER = (
        By.CSS_SELECTOR,
        'div[data-testid="bottom-buttons-panel"]',
    )

    DROPDOWN_BTN = (By.ID, "associate-dropdown-btn")
    DROPDOWN_CONTAINER = (By.ID, "dropdown-div")
    BMK_DATA = (By.CSS_SELECTOR, 'strong[data-testid="bmk-data"]')
    BMK_VIEW = (By.CSS_SELECTOR, 'a[data-testid="bmk-view"]')
    BMK_ASSOCIATE = (By.CSS_SELECTOR, 'button[data-testid="bmk-associate"]')
    NO_BMKS = (By.CSS_SELECTOR, 'li[data-testid="no-bmks"]')
    DISABLED_ASSOCIATE = (By.CSS_SELECTOR, 'button[data-testid="disabled-associate"]')
    NOTE = (By.CSS_SELECTOR, 'small[data-testid="associate-note"]')

    BMKS_ASSOCIATIONS = (
        By.CSS_SELECTOR,
        'div[data-testid="associations-container"] > div.card',
    )
    ASSOCIATIONS_CONTAINER = (
        By.CSS_SELECTOR,
        'div[data-testid="associations-container"]',
    )

    ASSOC_NAME = (By.CSS_SELECTOR, 'h5[data-testid="assoc-entity-name"]')
    ASSOC_ANCHOR = (By.CSS_SELECTOR, 'a[data-testid="assoc-entity-anchor"]')
    ASSOC_APPROVAL_LABEL = (
        By.CSS_SELECTOR,
        'strong[data-testid="assoc-approval-status-label"]',
    )
    ASSOC_APPROVAL = (By.CSS_SELECTOR, 'span[data-testid="assoc-approval-status"]')
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

    ASSOCIATION_CARDS = (By.CSS_SELECTOR, "div.card.association-card .card-title > a")

    RESUME_SCRIPT = (
        By.CSS_SELECTOR,
        'script[data-testid="resume-container-association"]',
    )

    def __init__(self, driver, container="", benchmark=""):
        super().__init__(driver)
        self.CONTAINER_BTN = (
            By.XPATH,
            f'//h5//a[@data-testid="cont-name" and contains(text(), "{container}")]',
        )
        self.ASSOCIATE_BTN = (
            By.XPATH,
            f'//li[.//strong[contains(text(), "{benchmark}")]]//button[contains(@class, "request-association-btn")]',
        )

    def request_association(self):
        self.click(self.DROPDOWN_BTN)
        self.click(self.ASSOCIATE_BTN)

    def get_association_cards_titles(self):
        return [i.text for i in self.driver.find_elements(*self.ASSOCIATION_CARDS)]
