from pydantic import BaseModel, Field, SecretStr
from selenium.webdriver import ChromeOptions

from browserbots.common.utils import (
    Capability,
    PageLoadStrategy,
    ParseArgsMixin,
    get_random_user_agent,
)


class Config(BaseModel, ParseArgsMixin):
    """
    Configuration for pointi job
    """

    email: SecretStr = Field(description="Login email")
    password: SecretStr = Field(description="Login password")
    chromedriver_executable_path: str = Field(
        default="chromedriver",
        description="Path to chromedriver binary (default: 'chromedriver')",
    )
    headless: bool = Field(
        default=False, description="Run in headless mode (default: False)"
    )
    no_sandbox: bool = Field(
        default=False,
        description=(
            "Set to True to run as root, inside docker container for example (default: "
            "False)"
        ),
    )
    page_load_strategy: PageLoadStrategy = Field(
        default=PageLoadStrategy.Eager,
        description="Selenium page load strategy (default: 'eager')",
    )
    dry_run: bool = Field(
        default=False,
        description=(
            "If True, do not actually click any unvisited links on the daily page "
            "(default: False)"
        ),
    )

    class Config:
        use_enum_values = True

    @classmethod
    def help(cls, field_name: str) -> str:
        for name, value in cls.schema().get("properties"):
            if name == field_name:
                return value.default("description", "")
        return ""

    @property
    def chrome_driver_kwargs(self):
        return dict(
            options=self._chrome_options,
            executable_path=self.chromedriver_executable_path,
        )

    @property
    def _chrome_options(self) -> ChromeOptions:
        user_agent = get_random_user_agent()
        opt = ChromeOptions()
        # The "normal" mode takes way too long for this website and problems finding
        # elements also arise for some reason. Eager seems to work fine. The "none" mode
        # is not able to find required elements.
        opt.set_capability(Capability.PageLoadStrategy, self.page_load_strategy)
        opt.headless = self.headless
        if self.no_sandbox:
            opt.add_argument("--no-sandbox")
        opt.add_argument(f"user-agent={user_agent}")
        return opt
