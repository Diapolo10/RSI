"""Light changer implementations."""

from __future__ import annotations

import contextlib
import logging
import socket
import time
from typing import TYPE_CHECKING

import requests
import yeelight  # type: ignore[import-untyped]

from rsi.colour import rgb_to_hsv
from rsi.types import LightChanger, Mode

if TYPE_CHECKING:
    from rsi.utils_.ConfigurationManager import ConfigurationManager

logger = logging.getLogger(__name__)


class HALightChanger:
    """Manage Home Assistant lights."""

    def __init__(self, home_assistant_ip: str, home_assistant_port: str | int) -> None:
        """Initialise Home Assistant light manager."""
        self.home_assistant_ip = home_assistant_ip
        self.home_assistant_port = home_assistant_port
        self.timeout = 10  # seconds

    def change_colour(self, red: int, green: int, blue: int) -> None:
        """Set Home Assistant light colour."""
        hue, saturation, value = rgb_to_hsv(red, green, blue)
        requests.post(
            f"http://{self.home_assistant_ip}:{self.home_assistant_port}/api/webhook/hsv-webhook"
            f"?H={hue}&S={saturation}&V={value}",
            timeout=self.timeout,
        )

    def default_colour(self) -> None:
        """Set Home Assistant light colour to default."""
        requests.post(
            f"http://{self.home_assistant_ip}:{self.home_assistant_port}/api/webhook/white-light",
            timeout=self.timeout,
        )


class WLEDLightChanger:
    """Manage WLED lights."""

    def __init__(self, wled_ip: str) -> None:
        """Initialise WLED light manager."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = 1
        self.timeout = 1
        self.MAX_LED_COUNT = 256
        self.UDP_IP_ADDRESS = wled_ip
        self.UDP_PORT_NO = 21324

    def change_colour(self, red: int, green: int, blue: int) -> None:
        """Set WLED light colour."""
        colour = (red, green, blue)
        logger.info("Changing color to %s", colour)

        colours = [colour for _ in range(self.MAX_LED_COUNT)]

        # Convert to WARLS Protocol
        data = bytearray([self.protocol, self.timeout])
        for idx, colour_ in enumerate(colours):
            data += bytearray([idx, *colour_])

        self.sock.sendto(data, (self.UDP_IP_ADDRESS, self.UDP_PORT_NO))
        logger.debug("Sending data to %s:%d", self.UDP_IP_ADDRESS, self.UDP_PORT_NO)

    def default_colour(self) -> None:
        """Set WLED light colour to default."""
        self.change_colour(255, 255, 255)


class YeeLightChanger:
    """Manage Yee lights."""

    def __init__(self, yee_light_ip: str) -> None:
        """Initialise Yee light manager."""
        # Connection taken from https://hyperion-project.org/forum/index.php?thread/529-xiaomi-rgb-bulb-simple-udp-server-solution/
        self.yee_light_ip = yee_light_ip
        self.bulb = yeelight.Bulb(self.yee_light_ip)
        try:
            self.bulb.turn_on()
        except OSError:
            logger.exception("Error turning on Yee bulb")
        self.bulb.effect = "smooth"  # can be "sudden" or "smooth"
        self.bulb.duration = 150  # miliseconds of duration of effect, ignored in "sudden" effect. MINIMUM 30!

        # Stop/Start music mode, bypasses lamp rate limits, ensures that previous sockets close before starting
        with contextlib.suppress(yeelight.BulbException):
            self.bulb.stop_music()
        time.sleep(1)
        while True:
            try:
                self.bulb.start_music()
                break
            except yeelight.BulbException:
                break
        time.sleep(1)

    def change_colour(self, red: int, green: int, blue: int) -> None:
        """Set Yee light colour."""
        hsv = rgb_to_hsv(red, green, blue)
        try:
            self.bulb.set_hsv(*hsv)
        except yeelight.BulbException:
            logger.exception("Error when attempting to set bulb colour")

    def default_colour(self) -> None:
        """Set Yee light colour to default."""
        try:
            self.bulb.set_color_temp(4700)
        except yeelight.BulbException:
            logger.exception("Error when attempting to set bulb to default settings")


class LightChangerResolver:
    """Resolve light changer."""

    def __init__(self, config_manager: ConfigurationManager) -> None:
        """Initialise changer resolver."""
        self.config_manager = config_manager

    def get_light_changer(self) -> LightChanger:
        """Get a light changer for the current mode."""
        config = self.config_manager.read()
        mode = config['MODE']['mode']
        if mode == Mode.HOME_ASSISTANT:
            home_assistant_ip = config['HOME ASSISTANT']['home_assistant_ip']
            home_assistant_port = config['HOME ASSISTANT']['home_assistant_port']
            return HALightChanger(home_assistant_ip, home_assistant_port)
        if mode == Mode.YEELIGHT:
            yeelight_ip = config['YEELIGHT']['yeelight_ip']
            return YeeLightChanger(yeelight_ip)
        if mode == Mode.WLED:
            wled_ip = config['WLED']['wled_ip']
            return WLEDLightChanger(wled_ip)

        msg = f"Unsupported mode '{mode}'."
        raise ValueError(msg)
