"""Type definitions."""

from enum import Enum
from typing import Protocol


class LightChanger(Protocol):
    """Protocol for changing light colours."""

    def change_colour(self, red: int, green: int, blue: int) -> None:
        """Set light colour."""

    def default_colour(self) -> None:
        """Set light colour to default."""


class Mode(str, Enum):
    """Light changer mode."""

    HOME_ASSISTANT = "homeassistant"
    WLED = "wled"
    YEELIGHT = "yeelight"
