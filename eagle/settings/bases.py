import json
import os
from typing import Dict, Any
from collections.abc import Mapping


class AppConfig(Mapping):

    def __init__(self, config: Dict | None):
        self._config = config

    def raw(self):
        return self._config

    def __getattr__(self, attr) -> Any:
        if attr not in self._config:
            return AppConfig(None)

        value = self._config[attr]

        if isinstance(value, dict):
            return AppConfig(value)

        if isinstance(value, list):
            return [AppConfig(item) if isinstance(item, dict) else item for item in value]

        return value

    def __getitem__(self, key) -> Any:
        return getattr(self, key)

    def __str__(self) -> str:
        try:
            return json.dumps(self._config)
        except Exception:
            return str(self._config)

    def __iter__(self):
        return iter(self._config)

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self._config)


class AppSettings:

    TOKEN_CACHE_FILE = os.path.join(os.path.expanduser("~/.eagle"), "token_cache.json")
    TOKEN_RETRY = 3


app_settings = AppSettings()
