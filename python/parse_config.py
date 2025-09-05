#!/usr/bin/env python3
# coding=utf-8
###############################################################################
"""
__author__ = "sunhn"

Description:
    config use yaml
    env vars from .env
"""

import logging
import re
import os
from dotenv import load_dotenv, dotenv_values
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)
ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)(?::-([^\}]+))?\}")


def load_dot_env_file(path: str = ".env", mode: str = "local", override: bool = False):
    """
    Load environment variables from a .env file.

    This function allows you to load environment variables into your application
    from a specified .env file. The loading behavior can be customized based on
    the mode parameter.

    Parameters:
    - path (str): The path to the .env file to be loaded. Defaults to ".env".
    - mode (str): The mode of loading.
        - "global": Loads the environment variables directly into the global environment.
        - "local": Returns the variables as a dictionary without affecting the global environment.
    - override (bool): If True, existing environment variables will be overridden by
      those loaded from the .env file. Ignored in "local" mode.

    Returns:
    - dict: A dictionary containing the environment variables if in "local" mode.
      None is returned if in "global" mode.
    """
    if mode == "global":
        load_dotenv(path, override=override)
        return dict(os.environ)  # return snapshot for consistency
    else:
        return dict(dotenv_values(path))


def load_yml(path: str) -> dict:
    """
    Load a YAML file and return a dict.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _merge_dict(base: dict, override: dict) -> dict:
    """
    Recursively merge two dictionaries.
    - Nested dicts are merged.
    - Values of different types or non-dict are overridden.
    - Returns a new merged dict without modifying the inputs.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def _replace_env_vars(obj, env_dict: dict):
    """
    Replace placeholders with environment variables inside dict/list/str.

    Supported syntax:
    - `${VAR_NAME}`: Replaced by the value of the environment variable `VAR_NAME`.
    - `${VAR_NAME:-default_value}`: If `VAR_NAME` is not set, `default_value` is used.
    - If an environment variable is not set and no default is provided, it is
      replaced with an empty string.
    """

    def replacer(match):
        var_name = match.group(1)
        default_val = match.group(2) or ""
        return str(env_dict.get(var_name, default_val))

    if isinstance(obj, dict):
        return {k: _replace_env_vars(v, env_dict) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_env_vars(i, env_dict) for i in obj]
    elif isinstance(obj, str):
        # m.group(1) is the variable name.
        # m.group(2) is the default value (or None).
        return ENV_VAR_PATTERN.sub(replacer, obj)
    else:
        return obj


class DotDict(dict):
    """
    dict with attribute-style access
    - cfg.app.url instead of cfg["app"]["url"]
    """

    def __getattr__(self, item):
        value = self.get(item)
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        return value

    __setattr__ = dict.__setitem__
    # __delattr__ = dict.__delitem__

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"No such attribute: {key}")

    def __dir__(self):
        """Enable tab completion of dict keys."""
        return list(self.keys()) + super().__dir__()


class Config:
    """
    Config loader with YAML + .env + environment variable support.

    Features:
    - Load one or more YAML files
    - Load .env variables (local or global)
    - Supports ${VAR:-default} syntax
    - Dot notation & dict-style access
    - Tab completion for keys
    - Priority: os.environ > .env > YAML
    """

    def __init__(self, yml_paths, env_dict: dict):
        if isinstance(yml_paths, str):
            yml_paths = [yml_paths]

        self.yml_paths = [Path(p) for p in yml_paths]
        self.env_dict = env_dict

        self._load_config()

    def _load_config(self):
        # 1. Merge YAML files
        merged = {}
        for path in self.yml_paths:
            data = load_yml(path)
            if data:
                merged = _merge_dict(merged, data)

        # 2. Replace env vars in YAML with .env first, then system env
        merged = _replace_env_vars(merged, self.env_dict)
        # merged = _replace_env_vars(merged, os.environ)

        # 3. Wrap in DotDict
        self._data = DotDict(merged)

    def __getattr__(self, item):
        return getattr(self._data, item)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __dir__(self):
        """Enable tab completion for top-level config keys."""
        return list(self._data.keys()) + super().__dir__()

    def __repr__(self):
        return f"Config({self._data})"


if __name__ == "__main__":
    pass
