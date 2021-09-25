from pydantic import Field, SecretStr
from selenium.webdriver import Chrome

from browserbots.common.utils import BotConfig, save_screenshot
from browserbots.honeygain import pages

LOGIN_PAGE_URI = "https://dashboard.honeygain.com"


class Config(BotConfig):
    """
    Configuration for honeygain job
    """

    email: SecretStr = Field(description="Login email")
    password: SecretStr = Field(description="Login password")
    dry_run: bool = Field(
        default=False,
        description="If True, do not actually click the honeypot link",
    )


def main(*, config: Config):
    logger = config.get_stdout_logger("honeygain.honeyjar")
    driver = Chrome(**config.chrome_driver_kwargs)
    logger.info("Starting job")

    try:
        driver.get(LOGIN_PAGE_URI)

        login = pages.LoginPage(driver=driver)
        login.login(
            email=config.email.get_secret_value(),
            password=config.password.get_secret_value(),
        )

        dash = pages.Dashboard(driver=driver)
        if dash.is_honey_jar_ready_to_open():
            logger.info("Honey jar is available. Opening.")
            dash.open_honey_jar()
        else:
            logger.info("Honey jar is not available.")

        logger.info("Job completed successfully")
        driver.quit()
    except Exception as e:
        save_screenshot(driver=driver)
        driver.quit()
        raise e


if __name__ == "__main__":
    main(config=Config.parse_args())
