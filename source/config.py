import orjson as json

import pathlib
import typing

def load_config(name: str) -> dict:
    config_path = pathlib.Path(__file__).parent.parent.resolve() / "configs" / f"{name}.json"
    with open(config_path, "rb") as f:
        config = json.loads(f.read())
    return config

def save_config(name: str, config: dict, pretty: bool = False):
    config_path = pathlib.Path(__file__).parent.parent.resolve() / "configs" / f"{name}.json"
    with open(config_path, "wb") as f:
        f.write(json.dumps(config, option=json.OPT_INDENT_2 if pretty else typing.Optional(int)))