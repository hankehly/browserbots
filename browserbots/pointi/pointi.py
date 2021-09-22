from pydantic import Field, SecretStr
from selenium.webdriver import Chrome

from browserbots.common.utils import BotConfig, PageLoadStrategy
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
    driver = Chrome(**config.chrome_driver_kwargs)
    driver.get(LOGIN_PAGE_URI)

    login = pages.LoginPage(driver=driver)

    login.login(
        email=config.email.get_secret_value(),
        password=config.password.get_secret_value(),
    )

    top = pages.TopPage(driver=driver)
    top.navigate_to_daily_page()

    daily = pages.DailyPage(driver=driver)
    daily.click_unvisited_links(dry_run=config.dry_run)
    daily.print_point_count()


if __name__ == "__main__":
    main(config=Config.parse_args())
