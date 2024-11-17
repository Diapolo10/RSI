"""Windows."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import PySimpleGUI as sg  # type: ignore[import-untyped]  # noqa: N813
import yeelight  # type: ignore[import-untyped]

from rsi.colour import get_average_screen_colour, get_screens_list
from rsi.types import Mode
from rsi.utils import find_bulbs

if TYPE_CHECKING:
    from rsi.light_changer import LightChangerResolver
    from rsi.utils_.ConfigurationManager import ConfigurationManager

logger = logging.getLogger(__name__)

class MainWindow:
    """Main window."""

    def __init__(self,
                 config_manager: ConfigurationManager,
                 light_changer_resolver: LightChangerResolver,
                 settings_window: SettingsWindow) -> None:
        """Initialise main window."""
        self.config_manager = config_manager
        self.settings_window = settings_window
        self.light_changer_resolver = light_changer_resolver
        self.light_changer = self.light_changer_resolver.get_light_changer()
        self.screens_list = get_screens_list()

    def render_layout(self, theme: str, refresh_rate: int, colour_precision: int) -> sg.Window:
        """Create UI elements."""
        sg.theme(theme)

        layout = [
            [
                sg.Text(
                    'Max Brightness:',
                    tooltip='The max brightness of the screen. When "Vary Brightess" is off,\
                          this change be the lamp brightness.',
                ),
                sg.Slider(
                    range=(1, 100),
                    default_value=100,
                    orientation='horizontal',
                    key="MAX-BRIGHTNESS",
                    tooltip='The max brightness of the screen. When "Vary Brightess" is off,\
                          this change be the lamp brightness.',
                ),
                sg.Checkbox(
                    'Vary Brightess',
                    default=True,
                    key="VARY-BRIGHTNESS",
                    tooltip='Toggles whether the brightness will vary depending on screen brightness.',
                ),
            ],
            [
                sg.Text(
                    'Refresh Rate:',
                    tooltip='Milliseconds between each screen capture',
                ),
                sg.Slider(
                    range=(0, 150),
                    default_value=refresh_rate,
                    orientation='horizontal',
                    enable_events=True,
                    key="REFRESH-RATE",
                    tooltip='Milliseconds between each screen capture',
                ),
                sg.Text(
                    'Color Precision:',
                    tooltip='The precision of the color capture. Lower values are faster (less CPU)\
                          but less accurate.',
                ),
                sg.Slider(
                    range=(0, 100),
                    default_value=colour_precision,
                    orientation='horizontal',
                    enable_events=True,
                    key="COLOR-PRECISION",
                    tooltip='The precision of the color capture. Lower values are faster (less CPU)\
                          but less accurate.',
                    ),
            ],
            [
                sg.Text(
                    'Screen:',
                    tooltip='The screen to be synced to the light.',
                ),
                sg.Combo(
                    values=self.screens_list,
                    default_value=self.screens_list[0],
                    disabled=len(self.screens_list) <= 2,  # noqa: PLR2004
                    auto_size_text=True,
                    key='SCREENS-LIST',
                ),
                sg.Button(
                    'Refresh Screens',
                    tooltip='Use this to refresh the screen list when connecting / disconnecting screens.',
                ),
                sg.Text(
                    'UI Theme:',
                    tooltip='The theme for the UI (I personally recommend HotDogStand).',
                ),
                sg.Combo(
                    values=sg.theme_list(),
                    default_value=theme,
                    auto_size_text=True,
                    enable_events=True,
                    key='THEME',
                    tooltip='The theme for the UI (I personally recommend HotDogStand).',
                ),
            ],
            [
                sg.Button('Start', tooltip = 'Starts the light sync.'),
                sg.Button('Stop', tooltip = 'Stops the light sync and goes back to default lighting.'),
                sg.Button('Settings', tooltip = 'Configure app settings.'),
            ],
        ]

        # Create the Window
        return sg.Window('Screen Light Thingy', layout)

    def show_main_window(self) -> None:  # noqa: C901
        """Display the main window."""
        config = self.config_manager.read()

        refresh_rate = int(config.get('ADVANCED', fallback={}).get('refresh_rate', fallback=0))
        colour_precision = int(config.get('ADVANCED', fallback={}).get('color_precision', fallback=20))
        self.config_manager.writeAdvancedConfig(refresh_rate, colour_precision)

        theme = config.get('UI', fallback={}).get('theme', fallback='reddit')
        self.config_manager.writeUIConfig(theme)


        window = self.render_layout(theme, refresh_rate, colour_precision)
        running = False # Wether the light sync is running or not

        while True:
            # I recommend using 150ms for YeeLight Mode and 1000ms on HA mode (higher latency)
            event, values = window.read(refresh_rate)
            # print(event, values) # Shows GUI state (for debugging)  # noqa: ERA001
            # max_br = values["MAX-BRIGHTNESS"]  # noqa: ERA001
            # vary_br = values["VARY-BRIGHTNESS"]  # noqa: ERA001
            sc = self.screens_list.index(values['SCREENS-LIST'])

            if event == 'Start': # if user clicks start
                running = True

            if event == sg.WIN_CLOSED: # if user closes window
                self.light_changer.default_colour()
                break

            if event == 'Stop': # if user clicks stop
                self.light_changer.default_colour()
                running = False

            if event == 'Refresh Screens': # if user clicks Refresh Screens
                self.screens_list = get_screens_list()
                window.Element('SCREENS-LIST').update(values = self.screens_list, set_to_index = [0])
                window.Element('SCREENS-LIST').update(disabled = len(self.screens_list) == 2)  # noqa: PLR2004

            if event == 'Settings': # if user clicks Settings
                self.settings_window.show_settings_window()
                self.light_changer = self.light_changer_resolver.get_light_changer()

            if event == 'REFRESH-RATE': # if user changes refresh rate
                refresh_rate = int(values['REFRESH-RATE'])
                self.config_manager.writeAdvancedConfig(refresh_rate, colour_precision)

            if event == 'COLOR-PRECISION': # if user changes color precision
                colour_precision = int(values['COLOR-PRECISION'])
                self.config_manager.writeAdvancedConfig(refresh_rate, colour_precision)

            if event == 'THEME': # if user changes theme
                theme = values['THEME']
                self.config_manager.writeUIConfig(theme)
                window.close()
                window = self.render_layout(theme, refresh_rate, colour_precision)

            if running:
                avg = get_average_screen_colour(sc, colour_precision)
                rgb = avg[0], avg[1], avg[2]
                self.light_changer.change_colour(*rgb)

        window.close()


class SettingsWindow:
    """Settings window."""

    def __init__(self, config_manager : ConfigurationManager, light_changer_resolver: LightChangerResolver) -> None:
        """Initialise settings screen."""
        self.config_manager = config_manager
        self.light_changer_resolver = light_changer_resolver
        self.light_changer = self.light_changer_resolver.get_light_changer()
        self.default_yeelight_ips = ['Press Discover to find bulbs!']

    def render_layout(self) -> sg.Window:
        """Create settings window layout."""
        config = self.config_manager.read()

        mode = config['MODE']['mode']
        home_assistant_ip = config['HOME ASSISTANT']['home_assistant_ip']
        home_assistant_port = config['HOME ASSISTANT']['home_assistant_port']
        yeelight_ip = config['YEELIGHT']['yeelight_ip']
        wled_ip = config['WLED']['wled_ip']

        mode_config_layout = []

        if mode == Mode.HOME_ASSISTANT:
            mode_config_layout = [
                [
                    sg.Text('Home Assistant IP', tooltip = 'The local address of your Home Assistant.'),
                    sg.InputText(default_text = home_assistant_ip, key = 'HOME-ASSISTANT-IP'),
                ],
                [
                    sg.Text('Home Assistant Port:', tooltip = 'The port of your Home Assistant (8123 by default).'),
                    sg.InputText(default_text = home_assistant_port, key = 'HOME-ASSISTANT-PORT'),
                ],
            ]
        elif mode == Mode.YEELIGHT:
            mode_config_layout = [
                [
                    sg.Text('Yeelight bulb IP', tooltip = 'The local address of your Yeelight lightbulb.'),
                    sg.InputText(default_text = yeelight_ip, key = 'YEELIGHT-IP'),
                ],
                [
                    sg.Text('Bulbs in your LAN', tooltip = 'Automatically discovered yeelight bulbs in your LAN.'),
                    sg.Button('Discover', tooltip = 'Automatically discovers yeelight bulbs in your LAN.'),
                    sg.Combo(
                        values=self.default_yeelight_ips,
                        disabled=self.default_yeelight_ips[0] == 'Press Discover to find bulbs!',
                        default_value=self.default_yeelight_ips[0],
                        expand_x=True,
                        auto_size_text=True,
                        enable_events=True,
                        key='DISCOVERED-BULBS-LIST',
                    ),
                ],
            ]
        elif mode == Mode.WLED:
            mode_config_layout = [
                [
                    sg.Text('WLED IP', tooltip = 'The local address of your WLED instance.'),
                    sg.InputText(default_text = wled_ip, key = 'WLED-IP'),
                ],
            ]

        modes = [mode.value for mode in Mode]

        default_buttons = [
                [
                    sg.Button('Default', tooltip = 'Returns all default values.'),
                    sg.Combo(
                        values=modes,
                        default_value=[mode],
                        auto_size_text=True,
                        key='MODE',
                        enable_events=True,
                        tooltip='Switches between yeelight mode to homme assistant mode.',
                    ),
                    sg.Button('Save', tooltip = 'Validates and saves the new configuration.'),
                    sg.Button('Cancel', tooltip = 'Closes the settings window.'),
                ],
            ]

        mode_config_layout.append(default_buttons)

        return sg.Window('Settings', mode_config_layout)

    def show_settings_window(self) -> None:  # noqa: C901
        """Display the settings window."""
        window = self.render_layout()

        while True:
            event, values = window.read()
            if event == 'DISCOVERED-BULBS-LIST':
                ip = values['DISCOVERED-BULBS-LIST']
                window.Element('YEELIGHT-IP').update(value = ip)
            if event == 'Discover':
                bulbs = find_bulbs()
                self.default_yeelight_ips = bulbs
                window.Element('DISCOVERED-BULBS-LIST').update(values = bulbs, value = bulbs[0], disabled = False)
            if event == 'Default':
                self.config_manager.default()
                window.close()
                window = self.render_layout()
            if event == 'MODE':
                mode = values['MODE']
                self.config_manager.writeMode(mode)
                window.close()
                window = self.render_layout()
            if event in ('Cancel', sg.WIN_CLOSED):
                break
            if event == 'Save':
                mode = values['MODE']
                if mode == Mode.HOME_ASSISTANT:
                    home_assistant_ip = values['HOME-ASSISTANT-IP']
                    home_assistant_port = values['HOME-ASSISTANT-PORT']
                    self.config_manager.writeHAConfig(home_assistant_ip, home_assistant_port)
                elif mode == Mode.YEELIGHT:
                    yeelight_ip = values['YEELIGHT-IP']
                    self.config_manager.writeYeelightConfig(yeelight_ip)
                elif mode == Mode.WLED:
                    wled_ip = values['WLED-IP']
                    self.config_manager.writeYeelightConfig(wled_ip)

                self.light_changer = self.light_changer_resolver.get_light_changer()

                try:
                    logger.info("Testing Configuration")
                    self.light_changer.change_colour(0, 255, 0)
                    time.sleep(1)
                    self.light_changer.default_colour()
                    break
                except (yeelight.BulbException, OSError):
                    if mode == Mode.HOME_ASSISTANT:
                        sg.popup(
                            'Reaching Home Assistant failed!',
                            'Validate your IP and Port and make sure your webhooks are configured correctly!',
                        )
                    elif mode == Mode.YEELIGHT:
                        sg.popup(
                            'Reaching Yeelight Bulb failed!',
                            'Validate your IP and make sure your bulb is on & connected!',
                        )
                    elif mode == Mode.WLED:
                        sg.popup(
                            'Reaching WLED failed!',
                            'Validate your IP and make sure your WLED instance is on!',
                        )

        window.close()
