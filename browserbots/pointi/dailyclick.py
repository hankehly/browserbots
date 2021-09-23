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
    dry_run: bool = Field(
        default=False,
        description=(
            "If True, do not actually click any unvisited links on the daily page "
            "(default: False)"
        ),
    )

    @classmethod
    def page_load_strategy(cls):
        return PageLoadStrategy.Eager


def main(*, config: Config):
    logger = config.get_stdout_logger("pointi.dailyclick")

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
        top.click_menu_link("毎日クリック")

        daily = pages.DailyPage(driver=driver)
        result = daily.click_unvisited_links(dry_run=config.dry_run)

        logger.info(
            f"Success! Clicked {result.unvisited} links. "
            f"{result.visited} link(s) were already clicked."
        )

        point_count = daily.get_point_count()
        logger.info(f"Current point count is {point_count}")
    except Exception as e:
        save_screenshot(driver=driver)
        driver.quit()
        raise e
    else:
        logger.info("Job completed successfully")
        driver.quit()


if __name__ == "__main__":
    main(config=Config.parse_args())
