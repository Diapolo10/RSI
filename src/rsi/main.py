"""Main entry point, remove if project is not an executable."""

import logging

from rsi.light_changer import LightChangerResolver
from rsi.logger import ROOT_LOGGER_NAME, setup_logging
from rsi.utils_.ConfigurationManager import ConfigurationManager
from rsi.windows import MainWindow, SettingsWindow

logger = logging.getLogger(ROOT_LOGGER_NAME)


def main() -> None:
    """Lorem Ipsum."""
    setup_logging()

    logger.debug("Initialising main program.")
    config_manager = ConfigurationManager()
    light_change_resolver = LightChangerResolver(config_manager)

    logger.debug("Components initialised.")

    settings_window = SettingsWindow(config_manager, light_change_resolver)

    logger.debug("Settings window initialised.")

    main_window = MainWindow(config_manager, light_change_resolver, settings_window)

    logger.debug("Main window initialised.")

    main_window.show_main_window()


if __name__ == '__main__':
    main()
