import colorsys
import json
import requests as rq
import time
import sys
import unicornhathd
import decimal
import math
from io import BytesIO
from datetime import datetime, timedelta

try:
    from dateutil import tz
except ImportError:
    sys.exit('This script requires the dateutil module\nInstall with: sudo pip install dateutil')

try:
    import portolan
except ImportError:
    sys.exit('This script requires the portolan module\nInstall with: sudo pip install portolan')

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    sys.exit('This script requires the pillow module\nInstall with: sudo pip install pillow')

try:
    import feedparser
except ImportError:
    sys.exit('This script requires the feedparser module\nInstall with: sudo pip install feedparser')


api_key = "YOUR OPENWEATHERMAP API KY HERE"

disp_units = "metric"

# Enter your lattitue & longitude here, for weather and moon phase functions.
latitude = 51
longitude = 0

# You should be able to change this to any RSS feed, but it will only pick the latest entry in that feed.
news_feed = "http://feeds.bbci.co.uk/news/rss.xml?edition=uk"

spacer = "* * * * * *"

dec = decimal.Decimal

# Choose a font.
#
# Use sudo apt install fontconfig & `fc-list` to show a list of installed fonts on your system,
# or `ls /usr/share/fonts/` and explore.
FONT = ('/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf', 10)
##FONT = ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
#
# sudo apt install fonts-freefont-ttf
# FONT = ('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 12)
#
# sudo apt install fonts-roboto
# FONT = ('/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf', 10)

def same_day(tposix, tomorrow=False):
    now = datetime.now(tz.tzlocal())
    if tomorrow:
        now += timedelta(days=1)
    utc = datetime.fromtimestamp(tposix, tz.UTC)
    local = utc.astimezone()
    return local.date() == now.date()

def get_weather(api_key, lat, lon, units=disp_units):
    resp = rq.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units}")
    if resp:
        current = json.loads(resp.content)
        current['wind_direction'] = portolan.point(current['wind']['deg'])  # Convert degrees to compass points
    else:
        current = False

    resp = rq.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units={units}")
    if resp:
        forecast = json.loads(resp.content)
    else:
        print(f"Failed to get forecast: {resp.status_code} | {resp.content}")
        forecast = False

    today = list(filter(lambda l: same_day(l['dt'], tomorrow=False), forecast['list']))
    if len(today) == 0:
        today = list(filter(lambda l: same_day(l['dt'], tomorrow=True), forecast['list']))

    high = -1000
    wind = 0
    wind_direction = 0
    description = ""
    weather_id = 0
    humidity = 0

    for fc in today:
        if fc['main']['temp'] > high:
            high = fc['main']['temp']
            wind = fc['wind']['speed']
            wind_direction = portolan.point(fc['wind']['deg'])  # Convert degrees to compass points
            description = fc['weather'][0]['description']
            weather_id = fc['weather'][0]['id']
            humidity = fc['main']['humidity']

    forecast = {
        'temp': high,
        'wind': wind,
        'wind_direction': wind_direction,
        'description': description,
        'id': weather_id,
        'humidity': humidity
    }

    return current, forecast

def get_sun_times(api_key, lat, lon):
    resp = rq.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}")
    if resp:
        data = json.loads(resp.content)
        sunrise = datetime.fromtimestamp(data['sys']['sunrise'], tz.UTC).astimezone(tz.tzlocal()).strftime('%H:%M')
        sunset = datetime.fromtimestamp(data['sys']['sunset'], tz.UTC).astimezone(tz.tzlocal()).strftime('%H:%M')
    else:
        sunrise = sunset = "N/A"
    return sunrise, sunset

def get_latest_news():
    feed = feedparser.parse(news_feed)
    if feed.entries:
        latest_news = feed.entries[0].title
    else:
        latest_news = "No news available."
    return latest_news

# The code for this function was taken from here, http://inamidst.com/code/moonphase.py , 
# All credits to Sean B. Palmer, thanks.
def get_moon_phase(now=None):
    """Returns the current moon phase as a string."""
    if now is None:
        now = datetime.now()

    diff = now - datetime(2001, 1, 1)
    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
    lunations = dec("0.20439731") + (days * dec("0.03386319269"))
    pos = lunations % dec(1)

    index = (pos * dec(8)) + dec("0.5")
    index = math.floor(index)

    phases = {
        0: "New Moon",
        1: "Waxing Crescent",
        2: "First Quarter",
        3: "Waxing Gibbous",
        4: "Full Moon",
        5: "Waning Gibbous",
        6: "Last Quarter",
        7: "Waning Crescent"
    }

    #return phases[int(index) & 7], round(float(pos), 3)
    return phases[int(index) & 7]


def display_moon_image():
    """Fetches moon phase, selects corresponding icon, and opens the image."""
    moon_icons = {
        "New Moon": "icons/new_moon.png",
        "Waxing Crescent": "icons/waxing_crescent.png",
        "First Quarter": "icons/first_quarter.png",
        "Waxing Gibbous": "icons/waxing_gibbous.png",
        "Full Moon": "icons/full_moon.png",
        "Waning Gibbous": "icons/waning_gibbous.png",
        "Last Quarter": "icons/last_quarter.png",
        "Waning Crescent": "icons/waning_crescent.png"
    }

    try:
        moon_phase = get_moon_phase()  # Retrieve the moon phase
        icon_path = moon_icons.get(moon_phase, "icons/default.png")  # Get the corresponding icon
        return Image.open(icon_path)  # Open and return the image
    except Exception as e:
        print(f"Error loading moon image: {e}")
        return None  # Return None if an error occurs


def get_icon(weather_id):
    if weather_id in range(200, 233):
        icon = '11d'
    elif weather_id in range(300, 322):
        icon = '09d'
    elif weather_id in range(500, 505):
        icon = '09d'
    elif weather_id == 511:
        icon = '13d'
    elif weather_id in range(520, 532):
        icon = '10d'
    elif weather_id in range(600, 623):
        icon = '13d'
    elif weather_id in range(701, 782):
        icon = '50d'
    elif weather_id == 800:
        icon = '01d'
    elif weather_id == 801:
        icon = '02d'
    elif weather_id == 802:
        icon = '03d'
    elif weather_id in range(803, 805):
        icon = '04d'

    url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
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

def display_micon(img):
    unicornhathd.rotation(180)
    unicornhathd.brightness(0.5)
    width, height = unicornhathd.get_shape()
    # Resize with high-quality resampling
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    # Enhance contrast slightly for better visibility
    img = ImageOps.autocontrast(img)
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

def current_text(current):
    c_text = "    {} Temp: {:0.0f} Feels Like: {:0.0f} Wind: {:0.1f} {} Humidity: {}% ".format(
        current['weather'][0]['description'], current['main']['temp'], current['main']['feels_like'], current['wind']['speed'], current['wind_direction'], current['main']['humidity'])
    return c_text

def forecast_text(forecast):
    fc_text = "    {} High: {:0.0f} Wind: {:0.1f} {} Humidity: {}%".format(
        forecast['description'], forecast['temp'], forecast['wind'], forecast['wind_direction'], forecast['humidity'])
    return fc_text

def display_date_time():
    now = datetime.now().strftime(" %d %B %Y - %H:%M")
    return now

def display_text(TEXT, font=FONT):
    width, height = unicornhathd.get_shape()
    unicornhathd.rotation(90)
    unicornhathd.brightness(0.5)
    text_x = 1
    text_y = 2
    font_file, font_size = font
    font = ImageFont.truetype(font_file, font_size)
    text_bbox = font.getbbox(TEXT)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_width += width + text_x
    image = Image.new('RGB', (text_width, max(height, text_height)), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((text_x, text_y), TEXT, fill=(255, 255, 255), font=font)
    for scroll in range(text_width - width):
        for x in range(width):
            hue = (x + scroll) / float(text_width)
            br, bg, bb = [int(n * 255) for n in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
            for y in range(height):
                pixel = image.getpixel((x + scroll, y))
                r, g, b = [float(n / 255.0) for n in pixel]
                r = int(br * r)
                g = int(bg * g)
                b = int(bb * b)
                unicornhathd.set_pixel(width - 1 - x, y, r, g, b)
        unicornhathd.show()
        time.sleep(0.025)
    unicornhathd.off()

def is_connected():
    try:
        rq.get("http://openweathermap.org", timeout=5)
        return True
    except rq.ConnectionError:
        return False

def main():
    while True:
        if is_connected():
            current, forecast = get_weather(api_key, latitude, longitude)
            sunrise, sunset = get_sun_times(api_key, latitude, longitude)
            moon_phase = get_moon_phase()
            ctext = current_text(current)
            ftext = forecast_text(forecast)
            current_icon = get_icon(current['weather'][0]['id'])
            forecast_icon = get_icon(forecast['id'])
            latest_news = get_latest_news()
            moon_pic = display_moon_image()
            t_end = time.time() + 60 * 6
            while time.time() < t_end:
                dnt = display_date_time()
                display_text(dnt)
                time.sleep(1)
                display_text(spacer)
                display_text("Current:-")
                time.sleep(0.5)
                display_icon(current_icon)
                time.sleep(4)
                display_text(ctext)
                display_text(spacer)
                display_text("Forecast:-")
                time.sleep(0.5)
                display_icon(forecast_icon)
                time.sleep(4)
                display_text(ftext)
                display_text(spacer)
                display_text(f" Sunrise: {sunrise} Sunset: {sunset} ")
                display_text(spacer)
                display_text(f" Moon Phase: {moon_phase} ")
                time.sleep(0.5)
                display_micon(moon_pic)
                time.sleep(4)
                display_text(spacer)
                display_text(f" Latest News: {latest_news} ")
                display_text(spacer)
        else:
            print("No internet connection. Pausing for 5 minutes.")
            time.sleep(300)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        unicornhathd.off()
        print("Killed by CTRL-C")
        sys.exit()
