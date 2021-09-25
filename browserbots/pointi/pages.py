import time
from typing import Any

from pydantic import BaseModel
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
        self.submit_btn.wait(self.driver).submit()


class TopPage(BasePage):
    def click_menu_link(self, link_text: str) -> None:
        link = WaitPageElement(
            condition=EC.element_to_be_clickable((By.LINK_TEXT, link_text))
        )
        link.wait(self.driver).click()


class DailyPageClickResult(BaseModel):
    visited: int
    unvisited: int


class DailyPage(BasePage):
    links = WaitPageElement(
        condition=EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, "クリック"))
    )

    point_count = WaitPageElement(
        condition=EC.presence_of_element_located((By.CSS_SELECTOR, ".pt_count"))
    )

    def _is_visited(self, link):
        return link.text.strip() == "クリック済みです"

    def _is_unvisited(self, link):
        return link.text.strip().startswith("クリックで")

    def click_unvisited_links(self, *, dry_run) -> DailyPageClickResult:
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

        return DailyPageClickResult(visited=visited_count, unvisited=len(unvisited))

    def get_point_count(self) -> str:
        return self.point_count.wait(self.driver).text


class MagazineList(BasePage):
    """
    https://pointi.jp/contents/magazine/
    """

    magazine_links = WaitPageElement(
        condition=EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#outer > ul a")
        )
    )

    def list_magazine_urls(self):
        # https://pointi.jp/contents/magazine/bene/
        # https://pointi.jp/contents/magazine/bene/?sub=cat
        # https://pointi.jp/contents/magazine/bene/?sub=dog
        # https://pointi.jp/contents/magazine/ichioshi/
        link_tags = self.magazine_links.wait(self.driver)
        urls = [link.get_attribute("href") for link in link_tags]
        return urls


class MagazineArticleListItem(BaseModel):
    el: Any

    @property
    def has_stamp_icon(self) -> bool:
        try:
            self.el.find_element_by_css_selector(".list_stamp_img")
            return True
        except NoSuchElementException:
            return False


class MagazineArticleList(BasePage):
    """
    https://pointi.jp/contents/magazine/bene/

    Notes
    -----
    Articles are sorted by ascending time you acquired the stamp, so if the first
    article already has a stamp, this means you've acquired ALL stamps.

    """

    link_list = WaitPageElement(
        condition=EC.element_to_be_clickable((By.ID, "link_list"))
    )

    def list_article_items(self) -> list[MagazineArticleListItem]:
        items = self.link_list.wait(self.driver).find_elements_by_tag_name("li")
        return [MagazineArticleListItem(el=el) for el in items]

    def click_nth_article_link(self, n: int):
        """
        N starts from 0!
        """
        self.list_article_items()[n].el.click()


class MagazineArticleDetail(BasePage):
    """
    https://pointi.jp/contents/magazine/bene/detail.php?sub=39&no=112225

    記事一覧へ戻る
    """

    continue_btn = WaitPageElement(
        condition=EC.element_to_be_clickable((By.ID, "move_page"))
    )

    stamp_list = WaitPageElement(
        condition=EC.presence_of_element_located((By.CSS_SELECTOR, "ul.stamp_box")),
    )

    def continue_to_next_page(self) -> None:
        self.continue_btn.wait(self.driver).click()

    def can_continue(self) -> bool:
        try:
            self.continue_btn.wait(self.driver)
            return True
        except TimeoutException:
            self.stamp_list.wait(self.driver)
            return False
