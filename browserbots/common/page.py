from typing import Any

from selenium.webdriver.support.ui import WebDriverWait
from pydantic import BaseModel, NonNegativeInt


class BasePage:
    def __init__(self, *, driver):
        self.driver = driver


class WaitPageElement(BaseModel):
    timeout: NonNegativeInt = 10
    condition: Any

    def wait(self, driver):
        return WebDriverWait(driver, self.timeout).until(self.condition)
