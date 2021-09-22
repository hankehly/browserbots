import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from browserbots.common.page import BasePage, WaitPageElement


class LoginPage(BasePage):
    input_mail = WaitPageElement(
        condition=EC.presence_of_element_located(
            (By.CSS_SELECTOR, "form[name='login'] input[name='email_address']")
        )
    )

    input_pass = WaitPageElement(
        condition=EC.presence_of_element_located(
            (By.CSS_SELECTOR, "form[name='login'] input[name='password']")
        )
    )

    submit_btn = WaitPageElement(
        condition=EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "form[name='login'] input[type='submit']")
        )
    )

    def login(self, *, email: str, password: str):
        self.input_mail.wait(self.driver).send_keys(email)
        self.input_pass.wait(self.driver).send_keys(password)
        self.submit_btn.wait(self.driver).click()


class TopPage(BasePage):
    link = WaitPageElement(
        condition=EC.element_to_be_clickable((By.LINK_TEXT, "毎日クリック"))
    )

    def navigate_to_daily_page(self):
        self.link.wait(self.driver).click()


class DailyPage(BasePage):
    links = WaitPageElement(
        condition=EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, "クリック"))
    )

    def print_point_count(self) -> None:
        point_count = self.driver.find_element_by_css_selector(".pt_count").text
        print(f"Current point count is {point_count}")

    def _is_visited(self, link):
        return link.text.strip() == "クリック済みです"

    def _is_unvisited(self, link):
        return link.text.strip().startswith("クリックで")

    def click_unvisited_links(self, *, dry_run) -> None:
        visited_count = 0
        unvisited = []

        for link in self.links.wait(self.driver):
            if self._is_visited(link):
                visited_count += 1
            elif self._is_unvisited(link):
                unvisited.append(link)

        if dry_run:
            print("Skipping link clicks (dry run)")
        else:
            for link in unvisited:
                link.click()
                time.sleep(1)

        print(f"Success! Clicked {len(unvisited)} links.")
        print(f"{visited_count} link(s) were already clicked.")
