"""Global config options of the package."""

import os
from importlib import resources as pkg_resources
from pathlib import Path

from dotenv import load_dotenv

import rsi

load_dotenv()

PACKAGE_NAME = "rsi"

with pkg_resources.as_file(pkg_resources.files(rsi)) as package_dir:
    DEFAULT_LOGGER_CONFIG_FILE_PATH = package_dir / 'logger_config.toml'
    DEFAULT_RSI_CONFIG_FILE_PATH = package_dir / 'rsi_config.toml'

LOGGER_CONFIG_FILE = Path(os.environ.get("RSI_LOGGER_CONFIG_FILE", DEFAULT_LOGGER_CONFIG_FILE_PATH))
RSI_CONFIG_FILE = Path(os.environ.get("RSI_CONFIG_FILE", DEFAULT_RSI_CONFIG_FILE_PATH))

# Prime numbers are used to get a more random sampling of the image (to avoid sampling the same pixels in a row)
PRIME_NUMBBERS = [
    1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79,
    83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269,
    271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373,
    379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467,
    479, 487, 491, 499, 503, 509, 521, 523, 541,
]

