from functools import lru_cache

from adapter.config.loader import load_config
from adapter.config.model import AppConfig


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    return load_config()
