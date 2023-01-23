import orjson as json

import pathlib

def load_config(name: str) -> dict:
    config_path = pathlib.Path(__file__).parent.parent.resolve() / "configs" / f"{name}.json"
    with open(config_path, "rb") as f:
        config = json.loads(f.read())
    return config