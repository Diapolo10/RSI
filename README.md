
# RSI

RSI = Room Screen Immersion

Syncs a smart bulb to the average screen color to get a beter immersion experience.  
Great for **movies** and **gaming**.

## Showcase Video

[![Watch the video](https://img.youtube.com/vi/LmSRSs_x13M/maxresdefault.jpg)](https://youtu.be/LmSRSs_x13M)

## Supported Modes

1. Yeelight Mode - Connects directly to a Yeelight smart bulb (UDP).
2. Home Assistant Mode - Sends a webhook call to your Home Assistant that updates your light to your average screen color.
3. WLED Mode - Connects directly to your local WLED instance (UDP). Will sync all LEDs on the WLED instance to the average screen color.

## Upcoming features

1. Dynamic screen sampling + light refresh rate that will be configurable from the GUI.
2. Yeelight bulb discovery that shows all bulbs in your LAN in the GUI.
3. Prettier GUI.
4. Bug fixes XD

### Advanced Configuration

In the config.ini file you can find some advanced configurations that have not been added to the UI yet.
The 2 advanced options that can elevate the sync experience are:

1. Refresh Rate - (0 to 1000) This is the time in milliseconds that will be waited between screenshots. I reccomend 0 for UDP modes such as Yeelight and WLED and around 150 for Webhook modes  such as Home Assistant.
2. Color Precision - (0 to 100) This is the sampling rate of the pixel colors from your screen. 0 = Sample all pixels. 100 = Sample every 541 pixles.

### Home Assistant Webhooks

You will need to add 2 webhooks to your Home Assistant for using Home Assistant Mode:

1. Default white light webhook - used to return the lightbulb to a default white color.

    ```yaml
    - alias: White Light
      description: ''
      trigger:
        - platform: webhook
          webhook_id: white-light
      condition: []
      action:
        - service: yeelight.set_color_temp_scene # This is the service used for Yeelight Bulbs. I'm sure other bulbs have a similar service.
          data:
            brightness: 100 # You can adjust these values to control the default light scene.
            kelvin: 4000 # You can adjust these values to control the default light scene.
          target:
            device_id: <YOUR DEVICES HOME-ASSITANT ID>
      mode: single
    ```

2. HSV color updater - used to update the lightbulb to a new HSV (Hue Saturation Lightness) value sent from RSI.

    ```yaml
    - alias: HSV Webhook
      description: ''
      trigger:
        - platform: webhook
          webhook_id: hsv-webhook
      condition: # This whole part can be removed. It just makes sure that your light is on before trying to update the color.
        - condition: device
          type: is_on
          device_id: <YOUR DEVICES HOME-ASSITANT ID>
          entity_id: <YOUR ENTITIES HOME-ASSITANT ID>
          domain: light
      action:
        - service: yeelight.set_hsv_scene
          data:
            hs_color:
              - '{{ trigger.query.H }}'
              - '{{ trigger.query.S }}'
            brightness: '{{ trigger.query.V }}'
          target:
            device_id: <YOUR DEVICES HOME-ASSITANT ID>
      mode: single

    ```

### Contribute

Feel free to contribute to this repository!

#### Building executable

1. Run `poetry install --with dev,linters`
2. Run `pip install pyinstaller`
3. Run `python3 -m PyInstaller --noconsole --onefile src/rsi/main.py`
