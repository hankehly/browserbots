from pydantic import Field, SecretStr
from selenium.webdriver import Chrome

from browserbots.common.utils import BotConfig, PageLoadStrategy, save_screenshot
from browserbots.pointi import pages

LOGIN_PAGE_URI = "https://pointi.jp/entrance.php"


class Config(BotConfig):
    """
    Configuration for pointi job
    """

    email: SecretStr = Field(description="Login email")
    password: SecretStr = Field(description="Login password")

    @classmethod
    def page_load_strategy(cls):
        return PageLoadStrategy.Eager


def main(*, config: Config):
    logger = config.get_stdout_logger("pointi.magazine")

    driver = Chrome(**config.chrome_driver_kwargs)
    logger.info("Starting job")

    try:
        driver.get(LOGIN_PAGE_URI)

        login = pages.LoginPage(driver=driver)

        login.login(
            email=config.email.get_secret_value(),
            password=config.password.get_secret_value(),
        )

        top = pages.TopPage(driver=driver)
        top.click_menu_link("読んで貯める!")

        magazines = pages.MagazineList(driver=driver)
        magazine_urls = magazines.list_magazine_urls()

        queue = magazine_urls.copy()

        logger.info("Added the following magazine URLs to work queue:")
        for i, url in enumerate(queue, start=1):
            logger.info(f"({i}) {url}")

        while queue:
            magazine_url = queue[0]

            logger.info(f"Navigating to magazine url: {magazine_url}")
            driver.get(magazine_url)

            article_list = pages.MagazineArticleList(driver=driver)
            articles = article_list.list_article_items()

            if articles[0].has_stamp_icon:
                logger.info(
                    f"Magazine ({magazine_url}) has no more unread articles. "
                    f"Continuing to next."
                )
                queue.pop(0)
                continue

            logger.info("Magazine has unread articles.")
            article_list.click_nth_article_link(0)
            detail = pages.MagazineArticleDetail(driver=driver)

            page_count = 0
            while detail.can_continue():
                page_count += 1
                detail.continue_to_next_page()

            logger.info(f"Finished {page_count} page article, continuing to next.")
    except Exception as e:
        save_screenshot(driver=driver)
        driver.quit()
        raise e
    else:
        logger.info("Job completed successfully")
        driver.quit()


if __name__ == "__main__":
    main(config=Config.parse_args())
