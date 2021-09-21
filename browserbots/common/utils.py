import argparse
import enum
import random
import time

from pydantic import BaseModel

from browserbots.common.settings import SCREENSHOTS_DIR

# Todo: Include more, move to separate text file
options = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
]


def get_random_user_agent() -> str:
    return random.choice(options)


class Capability:
    PageLoadStrategy = "pageLoadStrategy"


class PageLoadStrategy(str, enum.Enum):
    Normal = "normal"
    Eager = "eager"
    None_ = "none"


PYDANTIC_TYPE_TO_CALLABLE = {
    "string": str,
    "integer": int,
    "boolean": bool,
}


class ParseArgsMixin:
    @classmethod
    def parse_args(cls):
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
        instance = cls(**vars(args))

        return instance


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
