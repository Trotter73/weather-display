# weather-display
Weather display using a Raspberry Pi and Pimoroni Unicorn Hat HD

## Requirements
Hardware:
- Raspberry Pi (I used a Raspberry Pi 4)
- [Pimoroni Unicorn Hat HD](https://shop.pimoroni.com/products/unicorn-hat-hd)

Software:
- Python 3.x
  - dateutil
  - Pillow
  - [unicornhathd](https://github.com/pimoroni/unicorn-hat-hd)
  - requests
- [OpenWeather API Key](https://openweathermap.org/api)

## Running
First, add your OpenWeather API key to the file. Then, run as

```sh
$ python3 display-weather.py
```

Or, edit your crontab to start it up every morning. It will run for two hours then quit.

```sh
# crontab -e
```
```
# [...]
# m h  dom mon dow  command
  0 7  *   *   *    /usr/bin/python3 /path/to/display-weather.py
```
