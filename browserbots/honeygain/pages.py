import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from browserbots.common.page import BasePage, WaitPageElement


class LoginPage(BasePage):
    input_mail = WaitPageElement(
        condition=EC.presence_of_element_located(
            (By.CSS_SELECTOR, "form input[type='email']")
        )
    )

    input_pass = WaitPageElement(
        condition=EC.presence_of_element_located(
            (By.CSS_SELECTOR, "form input[type='password']")
        )
    )

    submit_btn = WaitPageElement(
        condition=EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "form button[type='submit']")
        )
    )

    def login(self, *, email: str, password: str):
        self.input_mail.wait(self.driver).send_keys(email)
        self.input_pass.wait(self.driver).send_keys(password)
        self.submit_btn.wait(self.driver).submit()


class Dashboard(BasePage):
    try_your_luck_button = WaitPageElement(
        condition=EC.element_to_be_clickable(
            (By.XPATH, "//button/span[text()='Try Your Luck!']")
        ),
        timeout=30,
    )

    open_honey_jar_button = WaitPageElement(
        condition=EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Open']"))
    )

    add_to_account_button = WaitPageElement(
        condition=EC.element_to_be_clickable(
            (By.XPATH, "//button/span[text()='ADD TO ACCOUNT']")
        )
    )

    def is_honey_jar_ready_to_open(self):
        """
        Check whether the "Try Your Luck!" button appears on the screen before the wait
        timeout expires.
        """
        try:
            self.try_your_luck_button.wait(self.driver)
            return True
        except TimeoutException:
            return False

    def open_honey_jar(self):
        """
        Go through the steps required to acquire daily winnings.
         1. Click the "Try Your Luck!" button
         2. Click the "Open" button
         3. Click the "ADD TO ACCOUNT" button

        The 3rd button starts with 0 size and gradually gets larger as an animation.
        To prevent the error "element has zero size" we add a small lag before
        attempting to click it. This is sufficient, but a more elegant approach would be
        to use selenium's "wait" feature and check for el.size until it becomes greater
        than 0.
        """
        self.try_your_luck_button.wait(self.driver).click()
        self.open_honey_jar_button.wait(self.driver).click()
        time.sleep(2)
        self.add_to_account_button.wait(self.driver).click()
