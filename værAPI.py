import json
import requests
import geopy
from geopy.geocoders import Nominatim
import socket
import datetime
from datetime import datetime, timedelta
import webbrowser

def getData():
    coords = getLocation()

    headers = {
        'User-Agent': 'MyTestApp/0.1',
    }

    params = {
        'lat': coords[0],
        'lon': coords[1],
    }

    url = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    filteredData = filterData(data)

    
    for entry in filteredData:
        print(entry)

    return filteredData


def getLocation():
  response = requests.get('https://ipinfo.io')
  data = response.json()
  location = data.get('loc').split(',')
  lat = location[0]
  lon = location[1]
  coords = [lat, lon]

  return coords


def filterData(data):
   
    current_time = datetime.now()
    time_offsets = [1, 6, 12]  
    filtered_data = []

    timeseries = data.get('properties', {}).get('timeseries', [])

    for t in timeseries:
        time_str = t.get('time')
        weather_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")

        
        time_difference = (weather_time - current_time).total_seconds() / 3600

        
        for offset in time_offsets:
            if abs(time_difference - offset) <= 0.5:
                filtered_data.append(t)

    return filtered_data

def formatWeatherData(data):
    formatted_data = {}
    
    for t in data:
        time_str = t.get('time')
        weather_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
        time_difference = (weather_time - datetime.now()).total_seconds() / 3600

        if abs(time_difference - 1) <= 0.5:
            formatted_data['1 time'] = t
        elif abs(time_difference - 6) <= 0.5:
            formatted_data['6 timer'] = t
        elif abs(time_difference - 12) <= 0.5:
            formatted_data['12 timer'] = t

    return formatted_data

def generateHTMLPage(formatted_data):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Værdata</title>
    </head>
    <body>
        <h1>Ditt nærområdet</h1>
    """

    for time_offset, data in formatted_data.items():
        
        weather_symbol_code = data['data']['next_1_hours']['summary']['symbol_code']

        
        weather_symbol_url = getWeatherSymbolURL(weather_symbol_code)

        html_content += f"""
        <h2>Vær data for {time_offset} fra nå:</h2>
        <img src="{weather_symbol_url}" alt="Weather Symbol">
        <p>Temperatur: {data['data']['instant']['details']['air_temperature']} °C</p>
        <p>Nedbør: {data['data']['next_1_hours']['details']['precipitation_amount']} mm</p>
        <p>Vindhastighet: {data['data']['instant']['details']['wind_speed']} m/s</p>
        <hr>
        """

    html_content += """
    </body>
    </html>
    """

    with open("weather_data.html", "w") as html_file:
        html_file.write(html_content)

    webbrowser.open("weather_data.html")

def getWeatherSymbolURL(symbol_code):
    symbol_mapping = {
     #download symbols from nrkno/yr github       
    "clearsky_day": "media/01d.png",
    "partlycloudy_day": "media/03d.png",
    "cloudy": "media/04.png",
    "rain": "media/09.png",
    "snow": "media/13.png",
    "fog": "media/15.png",
    "sleet": "media/12.png",
    "wind": "media/04.png",
    "partlycloudy_night": "media/03n.png",
    "rain_showers_day": "media/05d.png",
    "rain_showers_night": "media/05n.png",
    "sleet_showers_day": "media/07d.png",
    "sleet_showers_night": "media/07n.png",
    "snow_showers_day": "media/08d.png",
    "snow_showers_night": "media/08n.png",
    "thunder_rain_day": "media/06d.png",
    "thunder_rain_night": "media/06n.png",
    }

        
    

    
    return symbol_mapping.get(symbol_code, "media/15.png")

#not used for anything atm
def Vindretning():
    directions = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
    degrees = degrees % 360
    index = (round(((degrees + 360) if degrees < 0 else degrees) / 45) % 8)
    vind = directions[index]
    return vind

# Call getData() to get the filtered data
filtered_data = getData()

# Format and print the weather data
formatted_data = formatWeatherData(filtered_data)

# Generate and open the HTML page
generateHTMLPage(formatted_data)
