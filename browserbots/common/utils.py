import argparse
import enum
import logging
import random
import sys
import time

from pydantic import BaseModel, Field
from selenium.webdriver import ChromeOptions

from browserbots.common.settings import BASE_PACKAGE_PATH, SCREENSHOTS_DIR

USER_AGENTS_TXT = BASE_PACKAGE_PATH / "common" / "desktop_user_agents.txt"

PYDANTIC_TYPE_TO_CALLABLE = {
    "string": str,
    "integer": int,
    "boolean": bool,
}


def get_random_user_agent() -> str:
    with open(USER_AGENTS_TXT) as fo:
        return random.choice(fo.readlines()).strip()


def save_screenshot(*, driver, output_path: str = None):
    """
    Todo: Check behavior difference when headless vs not headless
    """
    if output_path is None:
        name = "screenshot-" + str(int(time.time() * 1000)) + ".png"
        output_path = str(SCREENSHOTS_DIR / name)
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
    width = driver.execute_script("return document.body.scrollWidth")
    height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(width, height)
    driver.save_screenshot(output_path)


class Capability:
    PageLoadStrategy = "pageLoadStrategy"


class PageLoadStrategy(str, enum.Enum):
    Normal = "normal"
    Eager = "eager"
    None_ = "none"


class ParseArgsMixin:
    """
    Provides a parse_args method to pydantic models
    """

    @classmethod
    def parse_args(cls):
        """
        Dynamically builds model using argparse library
        """
        assert issubclass(cls, BaseModel)

        schema = cls.schema()
        parser = argparse.ArgumentParser()

        for name, field in schema["properties"].items():
            arg_name = "--" + name.replace("_", "-")
            required = name in schema.get("required")
            default = cls.__fields__[name].get_default()
            help_text = field.get("description")
            action = "store"
            choices = None

            if "type" in field:
                type_callable = PYDANTIC_TYPE_TO_CALLABLE[field["type"]]
            elif "allOf" in field:
                # eg. "PageLoadStrategy"
                def_key = field["allOf"][0]["$ref"].rsplit("/", 1)[-1]
                # eg. {'title': 'PageLoadStrategy', 'description': 'An enumeration.',
                #      'enum': ['normal', 'eager', 'none'], 'type': 'string'}
                def_val = schema["definitions"][def_key]
                type_callable = PYDANTIC_TYPE_TO_CALLABLE[def_val["type"]]
                choices = def_val["enum"]
            else:
                raise ValueError(f"unknown field definition: {field}")

            if type_callable == PYDANTIC_TYPE_TO_CALLABLE["boolean"]:
                assert default is False, "boolean properties must default to False"
                action = "store_true"

            if isinstance(default, enum.Enum):
                default = default.value

            add_argument_kwargs = dict(
                default=default,
                required=required,
                help=help_text,
                dest=name,
            )

            if action == "store":
                add_argument_kwargs["type"] = type_callable
                add_argument_kwargs["choices"] = choices
            elif action == "store_true":
                add_argument_kwargs["action"] = action

            parser.add_argument(arg_name, **add_argument_kwargs)

        args = parser.parse_args()
        instance = cls.parse_obj(vars(args))

        return instance


class LogLevel(str, enum.Enum):
    Critical = "CRITICAL"
    Fatal = "FATAL"
    Error = "ERROR"
    Warning = "WARNING"
    Warn = "WARN"
    Info = "INFO"
    Debug = "DEBUG"
    NotSet = "NOTSET"


class BotConfig(BaseModel, ParseArgsMixin):
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
    log_level: LogLevel = LogLevel.Info

    class Config:
        use_enum_values = True

    @classmethod
    def page_load_strategy(cls):
        return PageLoadStrategy.Normal

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
        opt.set_capability(Capability.PageLoadStrategy, self.page_load_strategy())
        opt.headless = self.headless
        if self.no_sandbox:
            opt.add_argument("--no-sandbox")
        opt.add_argument(f"user-agent={user_agent}")
        return opt

    def get_stdout_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.log_level)
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
