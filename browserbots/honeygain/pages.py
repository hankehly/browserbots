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
        self.submit_btn.wait(self.driver).click()


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

    def open_honey_jar(self):
        self.try_your_luck_button.wait(self.driver).click()
        self.open_honey_jar_button.wait(self.driver).click()
        self.add_to_account_button.wait(self.driver).click()
