from typing import Any

from pydantic import BaseModel, NonNegativeInt
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, *, driver):
        self.driver = driver


class WaitPageElement(BaseModel):
    timeout: NonNegativeInt = 10
    condition: Any

    def wait(self, driver):
        return WebDriverWait(driver, self.timeout).until(self.condition)
