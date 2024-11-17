"""Colour functions."""

from __future__ import annotations

import logging

import mss
import numpy as np

from rsi.config import PRIME_NUMBBERS

logger = logging.getLogger(__name__)


def rgb_to_hsv(red: int, green: int, blue: int) -> tuple[int, float, float]:
    """Convert RGB to HSV."""
    r = red / 255
    g = green / 255
    b = blue / 255

    mx = max(r, g, b)
    mn = min(r, g, b)
    delta = mx-mn

    if mx == mn:
        h = 0.
    elif mx == r:
        h = (60 * ((g - b) / delta) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / delta) + 120) % 360
    else:
        h = (60 * ((r - g) / delta) + 240) % 360

    s = 0 if mx == 0 else delta / mx
    v = mx

    return round(h), round(s * 100, 1), round(v * 100, 1)

def get_screens_list() -> list[str | int]:
    """Get screens for GUI dropdown list."""
    with mss.mss() as sct:
        logger.info("Reading Screens:")

        # 0 - All monitors
        # 1 - Display 1
        # 2 - Display 2
        # And so on
        screens_list = []
        for idx, _ in enumerate(sct.monitors):
            logger.info("Display %d", idx)
            screens_list.append(idx or "All")

        return screens_list

def get_average_screen_colour(monitor_num: int, colour_precision: int) -> tuple[int, int, int]:
    """Calculate the average screen colour."""
    with mss.mss() as sct:
        sct_img = sct.grab(sct.monitors[monitor_num])

    # Save screenshot to file (commented so disabled)
    # mss.tools.to_png(sct_img.rgb, sct_img.size, output="test.png")  # noqa: ERA001

    # mss grabs the pictures as bgra, this code changes it to a RGB array
    frame = np.array(sct_img, dtype=np.uint8)
    rgb_img = np.flip(frame[:, :, :3], 2)

    # Calculating the average color numbers
    sample_rate = PRIME_NUMBBERS[colour_precision]  # Sample every sample_rate'th pixel.
    return np.average(rgb_img[::sample_rate], (0, 1))
