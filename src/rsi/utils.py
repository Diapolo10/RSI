"""Miscellaneous utility functions."""

from yeelight import discover_bulbs  # type: ignore[import-untyped]


def find_bulbs() -> list[str]:
    """Get list of discovered bulb IP addresses."""
    return [bulb['ip'] for bulb in discover_bulbs()]
