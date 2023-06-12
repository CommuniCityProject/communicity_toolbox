from typing import Union
from pathlib import Path
import collections.abc
import os
import re
import yaml


def update_dict(base: dict, new:dict) -> dict:
    """Update a dict recursively.

    Args:
        base (dict): The base dict to update.
        new (dict): Dict with the values to update.

    Returns:
        dict: `base` dict with the values of `new` dict updated.
    """
    for k, v in new.items():
        if isinstance(v, collections.abc.Mapping):
            base[k] = update_dict(base.get(k, {}), v)
        else:
            base[k] = v
    return base


def read_yaml(path: Union[str, Path]) -> dict:
    """Parse a yaml file.

    Args:
        path (Union[str, Path]): Path to a yaml file.

    Returns:
        dict: The parsed yaml
    """
    return yaml.safe_load(Path(path).read_text())


# Adapted from https://gist.github.com/mkaranasou/ba83e25c835a8f7629e34dd7ede01931
def read_yaml_env(path: Union[str, Path], tag: str = '!ENV') -> dict:
    """Load a yaml file and resolve the environment variables. The environment
    variables must have !ENV before them and be in the format: ${VAR_NAME}.
    (e.g. port: !ENV ${PORT})

    Args:
        path (Union[str, Path]): Path to the yaml file.
        tag (str, optional): Tag used to mark where to start searching for the
            environment variables. Defaults to '!ENV'.

    Returns:
        dict: The parsed yaml
    """
    # pattern for ${word}
    pattern = re.compile('.*?\${(\w+)}.*?')
    loader = yaml.SafeLoader
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables(loader, node):
        value = loader.construct_scalar(node)
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                full_value = full_value.replace(
                    f'${{{g}}}', os.environ.get(g, g)
                )
            try:
                if full_value.isdigit():
                    if "." in full_value:
                        return float(full_value)
                    return int(full_value)
                if full_value.lower() == "true":
                    return True
                if full_value.lower() == "false":
                    return False
                return full_value
            except:
                return full_value
        return value

    loader.add_constructor(tag, constructor_env_variables)

    with open(path, "r") as f:
        return yaml.load(f, Loader=loader)
    

def parse_config(path: Union[str, Path], parse_env: bool = True,
    parse_base: bool = True) -> dict:
    """Parse a config yaml file.

    Args:
        parse_env (bool, optional): Parse environment variables
            (e.g. !ENV ${PORT}). Defaults to True.
        parse_base (bool, optional): Parse the base config specified with
            '__BASE__: base/config/path.yaml'. Defaults to True.

    Returns:
        dict
    """
    BASE = "__BASE__"
    config = read_yaml_env(path) if parse_env else read_yaml
    if parse_base and BASE in config:
        base_path = Path(config[BASE])
        base_path = base_path if base_path.is_absolute() \
            else path.parent / base_path
        base_config = read_yaml(base_path)
        config = update_dict(config, base_config)
    return config
