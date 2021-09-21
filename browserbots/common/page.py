from typing import Any

from pydantic import BaseModel, NonNegativeInt
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from browserbots.common.utils import save_screenshot


class BasePage:
    def __init__(self, *, driver):
        self.driver = driver


class WaitPageElement(BaseModel):
    timeout: NonNegativeInt = 30
    condition: Any

    def wait(self, driver):
        try:
            return WebDriverWait(driver, self.timeout).until(self.condition)
        except TimeoutException as e:
            # During handling of the above exception, another exception occurred:
            #
            # Traceback (most recent call last):
            #   File "/Users/henryehly/src/browserbots/browserbots/pointi/pointi.py", line 30, in <module>
            #     main(config=config)
            #   File "/Users/henryehly/src/browserbots/browserbots/pointi/pointi.py", line 21, in main
            #     top.navigate_to_daily_page()
            #   File "/Users/henryehly/src/browserbots/browserbots/pointi/pages.py", line 40, in navigate_to_daily_page
            #     self.link.wait(self.driver).click()
            #   File "/Users/henryehly/src/browserbots/browserbots/common/page.py", line 23, in wait
            #     save_screenshot(driver=driver)
            #   File "/Users/henryehly/src/browserbots/browserbots/common/utils.py", line 105, in save_screenshot
            #     width = driver.execute_script("return document.body.scrollWidth")
            #   File "/Users/henryehly/src/browserbots/.venv/lib/python3.9/site-packages/selenium/webdriver/remote/webdriver.py", line 634, in execute_script
            #     return self.execute(command, {
            #   File "/Users/henryehly/src/browserbots/.venv/lib/python3.9/site-packages/selenium/webdriver/remote/webdriver.py", line 321, in execute
            #     self.error_handler.check_response(response)
            #   File "/Users/henryehly/src/browserbots/.venv/lib/python3.9/site-packages/selenium/webdriver/remote/errorhandler.py", line 242, in check_response
            #     raise exception_class(message, screen, stacktrace)
            # selenium.common.exceptions.JavascriptException: Message: javascript error: Cannot read properties of null (reading 'scrollWidth')
            #   (Session info: headless chrome=93.0.4577.82)
            save_screenshot(driver=driver)
            raise e
