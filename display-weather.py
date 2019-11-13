#!/usr/bin/env python3

import colorsys
from datetime import datetime, timedelta
from dateutil import tz
import json
import requests as rq
import time
from sys import exit
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    exit('This script requires the pillow module\nInstall with: sudo pip install pillow')

import unicornhathd


api_key = "your-openweathermap-api-key-here"
units="imperial"
FONT = ('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 12)


def same_day(tposix, tomorrow=False):
    now = datetime.now(tz.tzlocal())
    if tomorrow:
        now += timedelta(days=1)
    utc = datetime.fromtimestamp(tposix, tz.UTC)
    local = utc.astimezone()
    return local.date() == now.date()


def get_weather(api_key, city_id=5327684, units="imperial"):
    # Default city ID is Berkeley, CA
    resp = rq.get("https://api.openweathermap.org/data/2.5/weather?id={}&APPID={}&units={}".format(
                  city_id, api_key, units))
    if resp:
        current = json.loads(resp.content)
    else:
        current = False
    resp = rq.get("https://api.openweathermap.org/data/2.5/forecast?id={}&APPID={}&units={}".format(
                  city_id, api_key, units))
    if resp:
        forecast = json.loads(resp.content)
    else:
        forecast = False
    today = list(filter(lambda l: same_day(l['dt'], tomorrow=False), forecast['list']))
    if len(today) == 0:
        today = list(filter(lambda l: same_day(l['dt'], tomorrow=True), forecast['list']))
    high = -1000  # Below 0K
    wind = 0
    description = ""
    weather_id = 0
    for fc in today:
        if fc['main']['temp'] > high:
            high = fc['main']['temp']
            wind = fc['wind']['speed']
            description = fc['weather'][0]['description']
            weather_id = fc['weather'][0]['id']
    forecast = {'temp': high, 'wind': wind, 'description': description, 'id': weather_id}
    return current, forecast


def get_icon(weather_id):
    if weather_id < 300:
        icon = '11d'  # Thunderstorm
    elif weather_id < 400:
        icon = '09d'  # Drizzle
    elif weather_id < 511:
        icon = '10d'  # Rain
    elif weather_id < 520:
        icon = '13d'  # Freezing Rain
    elif weather_id < 600:
        icon = '09d'  # Shower Rain
    elif weather_id < 700:
        icon = '13d'  # Snow
    elif weather_id == 800:
        icon = '01d'  # Clear
    elif weather_id == 801:
        icon = '02d'  # Few Clouds
    elif weather_id == 802:
        icon = '03d'  # Scattered Clouds
    elif weather_id < 805:
        icon = '04d'  # Overcast Clouds
    url = "http://openweathermap.org/img/wn/{}@2x.png".format(icon)
    resp = rq.get(url)
    if resp:
        img = Image.open(BytesIO(resp.content))
    else:
        img = None
    return img


def display_icon(img):
    unicornhathd.rotation(180)
    unicornhathd.brightness(0.5)
    width, height = unicornhathd.get_shape()
    img = ImageOps.fit(img, (width, height), bleed=0.15)
    valid = False
    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((y, x))
            r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
            if r or g or b:
                valid = True
            unicornhathd.set_pixel(x, y, r, g, b)

    if valid:
        unicornhathd.show()


def build_text(current, forecast):
    text = "Temp: {:0.0f} Wind: {:0.1f} ".format(current['main']['temp'], current['wind']['speed'])
    text += "Forecast: {} High: {:0.0f}".format(forecast['description'], forecast['temp'])
    return text


def display_text(TEXT, font=FONT):
    # Use `fc-list` to show a list of installed fonts on your system,
    # or `ls /usr/share/fonts/` and explore.
    
    # sudo apt install fonts-droid
    # FONT = ('/usr/share/fonts/truetype/droid/DroidSans.ttf', 12)
    
    # sudo apt install fonts-roboto
    # FONT = ('/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf', 10)
    
    # ================ Now, let's draw some amazing rainbowy text! ===================
    
    # Get the width/height of Unicorn HAT HD.
    # These will normally be 16x16 but it's good practise not to hard-code such numbers,
    # just in case you want to try and hack together a bigger display later.
    width, height = unicornhathd.get_shape()
    
    unicornhathd.rotation(90)
    unicornhathd.brightness(0.5)
    
    # We want to draw our text 1 pixel in, and 2 pixels down from the top left corner
    text_x = 1
    text_y = 2
    
    # Grab our font file and size as defined at the top of the script
    font_file, font_size = font
    
    # Load the font using PIL's ImageFont
    font = ImageFont.truetype(font_file, font_size)
    
    # Ask the loaded font how big our text will be
    text_width, text_height = font.getsize(TEXT)
    
    # Make sure we accommodate enough width to account for our text_x left offset
    text_width += width + text_x
    
    # Now let's create a blank canvas wide enough to accomodate our text
    image = Image.new('RGB', (text_width, max(height, text_height)), (0, 0, 0))
    
    # To draw on our image, we must use PIL's ImageDraw
    draw = ImageDraw.Draw(image)
    
    # And now we can draw text at our desited (text_x, text_y) offset, using our loaded font
    draw.text((text_x, text_y), TEXT, fill=(255, 255, 255), font=font)
    
    # To give an appearance of scrolling text, we move a 16x16 "window" across the image we generated above
    # The value "scroll" denotes how far this window is from the left of the image.
    # Since the window is "width" pixels wide (16 for UHHD) and we don't want it to run off the end of the,
    # image, we subtract "width".
    for scroll in range(text_width - width):
        for x in range(width):
    
            # Figure out what hue value we want at this point.
            # "x" is the position of the pixel on Unicorn HAT HD from 0 to 15
            # "scroll" is how far offset from the left of our text image we are
            # We want the text to be a complete cycle around the hue in the HSV colour space
            # so we divide the pixel's position (x + scroll) by the total width of the text
            # If this pixel were half way through the text, it would result in the number 0.5 (180 degrees)
            hue = (x + scroll) / float(text_width)
    
            # Now we need to convert our "hue" value into r,g,b since that's what colour space our
            # image is in, and also what Unicorn HAT HD understands.
            # This list comprehension is just a tidy way of converting the range 0.0 to 1.0
            # that hsv_to_rgb returns into integers in the range 0-255.
            # hsv_to_rgb returns a tuple of (r, g, b)
            br, bg, bb = [int(n * 255) for n in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
    
            # Since our rainbow runs from left to right along the x axis, we can calculate it once
            # for every vertical line on the display, and then re-use that value 16 times below:
    
            for y in range(height):
                # Get the r, g, b colour triplet from pixel x,y of our text image
                # Our text is white on a black background, so these will all be shades of black/grey/white
                # ie 255,255,255 or 0,0,0 or 128,128,128
                pixel = image.getpixel((x + scroll, y))
    
                # Now we want to turn the colour of our text - shades of grey remember - into a mask for our rainbow.
                # We do this by dividing it by 255, which converts it to the range 0.0 to 1.0
                r, g, b = [float(n / 255.0) for n in pixel]
    
                # We can now use our 0.0 to 1.0 range to scale our three colour values, controlling the amount
                # of rainbow that gets blended in.
                # 0.0 would blend no rainbow
                # 1.0 would blend 100% rainbow
                # and anything in between would copy the anti-aliased edges from our text
                r = int(br * r)
                g = int(bg * g)
                b = int(bb * b)
    
                # Finally we colour in our finished pixel on Unicorn HAT HD
                unicornhathd.set_pixel(width - 1 - x, y, r, g, b)
    
        # Finally, for each step in our scroll, we show the result on Unicorn HAT HD
        unicornhathd.show()
    
        # And sleep for a little bit, so it doesn't scroll too quickly!
        time.sleep(0.025)
    
    unicornhathd.off()


def main():
    current, forecast = get_weather(api_key)
    icon = get_icon(forecast['id'])
    t0 = time.time()
    while True:
        display_icon(icon)
        time.sleep(10)
        text = build_text(current, forecast)
        display_text(text)
        if time.time() - t0 > 3600 * 2:
            display_icon(icon)
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        unicornhathd.off()
    exit(0)
    
