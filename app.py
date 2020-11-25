import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)
load_dotenv()
API_KEY = os.getenv('API_KEY')

pp = PrettyPrinter(indent=4)


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    q = request.args.get('city')
    units = request.args.get('units')

    url = 'http://api.openweathermap.org/data/2.5/weather'

    params = {
        'q' : q,
        'units' : units,
        'appid' : API_KEY
    }

    result_json = requests.get(url, params=params).json()

    # Uncomment the line below to see the results of the API call!
    pp.pprint(result_json)

    city = result_json['name']
    description = result_json['weather'][0]['description']
    temp = result_json['main']['temp']
    humidity = result_json['main']['humidity']
    wind_speed = result_json['wind']['speed']
    sunrise = datetime.fromtimestamp(result_json['sys']['sunrise'])
    sunset = datetime.fromtimestamp(result_json['sys']['sunset'])
    units_letter = get_letter_for_units(units)
    date = datetime.now(tz=None)

    context = {
        'date' : date,
        'city' : city,
        'description' : description,
        'temp' : temp,
        'humidity' : humidity,
        'wind_speed' : wind_speed,
        'sunrise' : sunrise,
        'sunset' : sunset,
        'units_letter' : units_letter
    }

    return render_template('results.html', **context)

def get_min_temp(results):
    """Returns the minimum temp for the given hourly weather objects."""
    # TODO: Fill in this function to return the minimum temperature from the
    # hourly weather data.
    # Variable = ['hourly']['temp'] (list??)
    # For lowest in variable
        #calculate which is the lowest 
        #return the lowest number 
    return results['main']['temp_min']

def get_max_temp(results):
    """Returns the maximum temp for the given hourly weather objects."""
    return results['main']['temp_max']


def get_lat_lon(city_name):
    geolocator = Nominatim(user_agent='Weather Application')
    location = geolocator.geocode(city_name)
    if location is not None:
        return location.latitude, location.longitude
    return 0, 0

@app.route('/historical_results')
def historical_results():
    """Displays historical weather forecast for a given day."""
    # city = request.args.get('city')
    units = request.args.get('units')
    date = request.args.get('date')
    city = request.args.get('city')

    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date_in_seconds = date_obj.strftime('%s')

    latitude, longitude = get_lat_lon('city')
    units_letter = get_letter_for_units(units)



    url = 'http://api.openweathermap.org/data/2.5/onecall/timemachine'
    params = {
        'appid' : API_KEY,
        'lat' : latitude,
        'lon' : longitude,
        'dt' : date_in_seconds,
        'units' : units,

        # TODO: Enter query parameters here for the 'appid' (your api key),
        # latitude, longitude, units, & date (in seconds).
        # See the documentation here (scroll down to "Historical weather data"):
        # https://openweathermap.org/api/one-call-api
        
    }
    
    result_json = requests.get(url, params=params).json()

    # Uncomment the line below to see the results of the API call!
    pp.pprint(result_json)

    result_current = result_json['current']
    # result_hourly = result_json['hourly']

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the 'result_current' object above.

    city = request.args.get('city')
    description = result_current['weather'][0]['description']
    temp = result_current['temp']
    # min_temp = get_min_temp(result_json)
    # max_temp = get_max_temp(result_json)

    context = {
        'city': city,
        'date': date_obj,
        'date' : date,
        'lat': latitude,
        'lon': longitude,
        'units_letter': units_letter,
        'description': description,
        'units' : units,
        'temp' : temp
        # 'min_temp' : min_temp,
        # 'max_temp' : max_temp
    }

    return render_template('historical_results.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
