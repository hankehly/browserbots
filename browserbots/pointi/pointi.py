from selenium.webdriver import Chrome
from browserbots.pointi.config import Config
from browserbots.pointi import pages

LOGIN_PAGE_URI = "https://pointi.jp/entrance.php"


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
    config = Config.parse_args()
    main(config=config)
