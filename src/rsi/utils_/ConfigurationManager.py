"""Configure the RSI application."""

from __future__ import annotations

import configparser
import logging
from typing import TYPE_CHECKING

import rtoml  # noqa: F401

from rsi.config import RSI_CONFIG_FILE  # noqa: F401

if TYPE_CHECKING:
    from rsi.types import Mode

logger = logging.getLogger(__name__)


class ConfigurationManager:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()

    def writeMode(self, mode: Mode) -> None:
        self.config['MODE'] = {'mode': mode}
        with open('config.ini', 'w+') as configfile:
            self.config.write(configfile)

    def writeHAConfig(self, home_assistant_ip, home_assistant_port) -> None:
        self.config['HOME ASSISTANT'] = {'home_assistant_ip': home_assistant_ip, 'home_assistant_port': home_assistant_port}
        with open('config.ini', 'w+') as configfile:
            self.config.write(configfile)

    def writeYeelightConfig(self, yeelight_ip) -> None:
        self.config['YEELIGHT'] = {'yeelight_ip': yeelight_ip}
        with open('config.ini', 'w+') as configfile:
            self.config.write(configfile)

    def writeWLEDConfig(self, wled_ip) -> None:
        self.config['WLED'] = {'wled_ip': wled_ip}
        with open('config.ini', 'w+') as configfile:
            self.config.write(configfile)

    def writeAdvancedConfig(self, refresh_rate, color_precision) -> None:
        self.config['ADVANCED'] = {'refresh_rate': refresh_rate, 'color_precision': color_precision}
        with open('config.ini', 'w+') as configfile:
            self.config.write(configfile)

    def writeUIConfig(self, theme) -> None:
        self.config['UI'] = {'theme': theme}
        with open('config.ini', 'w+') as configfile:
            self.config.write(configfile)

    def default(self) -> None:
        self.writeMode('WLED')
        self.writeHAConfig('192.168.1.123', '8123') # Default home assistant values
        self.writeYeelightConfig('192.168.1.200') # Random made up IP
        self.writeWLEDConfig('192.168.1.229') # Random made up IP
        self.writeAdvancedConfig('0', '50')
        self.writeUIConfig('reddit')

    def read(self) -> configparser.ConfigParser:
        """Read configuration to memory."""
        try:
            if not self.config.read('config.ini'):
                logger.warning('Reading config failed, writing new config instead.')
                self.default()
        except OSError:
            logger.exception('Reading config failed, writing new config instead.')
            self.default()
        return self.config
