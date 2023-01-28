from orjson import loads, dumps, OPT_INDENT_2
from pathlib import Path
from typing import Optional
from functools import lru_cache


@lru_cache(maxsize=5)
def load_config(name: str) -> dict:
    """Load a config file from the configs folder."""
    config_path = Path(
        __file__).parent.parent.resolve() / "configs" / f"{name}.json"
    with open(config_path, "rb") as f:
        config = loads(f.read())
    return config


def save_config(name: str, config: dict, pretty: bool = False) -> None:
    """Save a config file to the configs folder."""
    config_path = Path(
        __file__).parent.parent.resolve() / "configs" / f"{name}.json"
    with open(config_path, "wb") as f:
        f.write(dumps(
            config, option=OPT_INDENT_2 if pretty else Optional(int)))
