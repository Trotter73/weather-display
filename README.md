# Display Weather 2025

Building on the work of Josh Sanz, Display Weather 2025 takes his excellent work and adds some extra functionality that I thought would be useful.

# What's added -
The weather display section now includes the wind direction.

Current sunrise and sunset times are displayed.

Current moon phase is displayed.

Current date and time are displayed.

The latest article from an RSS feed of your choice is displayed.

Some additional checks for missing modules.

Some detection to prevent the script from dying if there isn't a net connection. 

# What's changed -
I changed the script to use latitude & longitude rather than city ID for no other reason other than that I use them elsewhere....

Now runs until you kill it, rather than exiting after 2 hours.

font.getsize is being depreciated so changed to font.getbox, not a drop in replacement unfortunately.

A lot of the comments were removed, simply because it made my hacking easier, sorry....

Ranges used to determine the weather icons (get_icon function), not used ranges like this before so was playing.

Probably other stuff as well...

# Requirements - 
The following python modules are needed on top of what was required originally...

feedparser <- Grabs the RSS feed and does a lot of the hard work there.

ephem      <- Works out the moon phase for you, could have used it for the sun functions as well but......

portolan   <- Changes degrees to compass points, nicer to read.


# Other stuff -
The script does not always clean up when exiting, especially when being run as a service, not sure why, if you know get in touch, anyway, hatoff.py can be run if you exit and are left with the lights on.

I found some fonts are hard to read, during my limited messing about I found Roboto-Medium.ttf seemed to be the cleanest.

# Todo -
Maybe migrate to using the PyOWM module and V3.0 or OneCall ?

I did think adding a quote of the day RSS feed in as well or maybe an exchange rate, but thought I was stretching the readability as it was...…

Moon phase icons rather than the text? If anyone has some nice free icons I would give it a go. 

----------------------------------------------------------------------------------------------------------------------------------------------------------------

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
