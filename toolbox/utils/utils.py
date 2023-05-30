import functools
import hashlib
import logging
import math
import random
import string
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


def random_string(length: int = 8) -> str:
    """Create a random strings with digits and upper and lower case letters.

    Args:
        length (int, optional): Length of the generated string.. Defaults to 8.

    Returns:
        str: A random string.
    """
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def float_or_none(value: any):
    """Tries to convert a value to float. If fails return None.
    """
    try:
        return float(value)
    except:
        return None


def str_separator(length: int = 80, title: str = "",
    char: str = "-", new_line: bool = True) -> str:
    """Create a separator string with an optional title.
    e.g: --------title--------

    Args:
        length (int, optional): Total character-length of the string.
            Defaults to 80.
        title (str, optional): Optional separator title. Defaults to "".
        char (str, optional): Character used for the separator.
            Defaults to "-".
        new_line (bool, optional): Add a new line at the end. Defaults to True.

    Returns:
        str: The separator string.
    """
    
    l2 = (length - len(title)) / 2
    r = char * math.floor(l2)
    r += title
    r += char * math.ceil(l2)
    if new_line:
        r += "\n"
    return r


def is_url(url: str) -> bool:
    """Check if a string is a valid URL.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def urljoin(*args: str) -> str:
    """Join the given arguments into a url. Trailing but not leading slashes
    are stripped for each argument.
    """
    return "/".join(map(lambda x: str(x).rstrip("/").strip("/"), args))


class _LoggingFormatter(logging.Formatter):
    """Logging colored formatter,
    adapted from https://stackoverflow.com/a/56944256/3638629
    """

    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    date_format = "%Y-%d-%m %H:%M:%S"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.date_format)
        return formatter.format(record)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get the default logger.

    Args:
        name (Optional[str], optional): Name of the logger. Defaults to None.

    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    ch.setFormatter(_LoggingFormatter())
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.addHandler(ch)
    logger.propagate = False
    return logger


def hash_str(value: str, algorithm="sha1") -> str:
    """Return the hash of a string.

    Args:
        value (str): The string to hash.
        algorithm (str, optional): Name of the hash algorithm.
            One of ["md5","sha1","sha224","sha256","sha384","sha512"]
            Defaults to "sha1".

    Raises:
        ValueError: If algorithm is not recognized.

    Returns:
        str: The hash string.
    """
    valid_algorithms = ("md5","sha1","sha224","sha256","sha384","sha512")
    if algorithm not in valid_algorithms:
        raise ValueError(f"Algorithm must be one of {valid_algorithms} " \
            f"({algorithm})")
    hasher = getattr(hashlib, algorithm)
    return hasher(value.encode()).hexdigest()


@functools.cache
def get_version():
    version_file = Path(__file__).parent.parent.joinpath("version")
    return version_file.read_text()
