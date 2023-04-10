import json
import requests
from flask import Flask, request, jsonify
from flasgger import Swagger
import jwt  

app = Flask(__name__)
# Set swagger configuration
swagger = Swagger(app, template_file='swagger.json', config={})


# AccuWeather API key
API_KEY = 'WuyjMmcckuGC6uGURGq3Avg10fps4DyW'  # Replace with your AccuWeather API key


@app.route('/')
def index():
    return "Weather App"


@app.route('/weather', methods=['POST'])
def get_weather():
    """
    Get weather information for a city.

    ---
    parameters:
      - name: city_name
        in: formData
        type: string
        required: true
        description: Name of the city for which weather information is required.
    responses:
      200:
        description: Weather information for the city.
        schema:
          type: object
          properties:
            city:
              type: string
              description: City name
            temperature:
              type: number
              description: Current temperature in Celsius
            description:
              type: string
              description: Weather description
            humidity:
              type: number
              description: Relative humidity
            pressure:
              type: number
              description: Atmospheric pressure in millibars
            wind_speed:
              type: number
              description: Wind speed in kilometers per hour
      404:
        description: City not found
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message
      500:
        description: Failed to get weather data
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message
    """
     
    city_name = request.form['city_name']
    location_key = get_location_key(city_name)
    if location_key is None:
        return jsonify(error='City not found'), 404
    else:
        weather_data = get_weather_data(location_key)
        if weather_data is None:
            return jsonify(error='Failed to get weather data'), 500
        else:
            return jsonify(weather_data)


def get_location_key(city_name):
    url = f'https://dataservice.accuweather.com/locations/v1/cities/autocomplete'
    params = {
        'apikey': API_KEY,
        'q': city_name
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['Key']
    return None


def get_weather_data(location_key):
    url = f'https://dataservice.accuweather.com/currentconditions/v1/{location_key}'
    params = {
        'apikey': API_KEY,
        'details': 'true'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            weather_data = {
                #'city': data[0]['LocalizedName'],
                'temperature': data[0]['Temperature']['Metric']['Value'],
                'description': data[0]['WeatherText'],
                'humidity': data[0]['RelativeHumidity'],
                'pressure': data[0]['Pressure']['Metric']['Value'],
                'wind_speed': data[0]['Wind']['Speed']['Metric']['Value']
            }
            return weather_data
    return None

@app.route('/cities', methods=['GET'])
def get_cities():
    """
    Get cities from AccuWeather API using autocomplete endpoint.
    :param query: The search query for cities.
    :return: List of cities in JSON format with city key and country key.
    """
    query = request.args.get('query')
    base_url = "http://dataservice.accuweather.com/locations/v1/cities/autocomplete"
    params = {
        "q": query,
        "apikey": API_KEY # Replace with your actual API key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        cities = json.loads(response.text)
        formatted_cities = []
        for city in cities:
            formatted_city = {
                "city_key": city["Key"],
                "city": city["LocalizedName"],
                "country_key": city["Country"]["ID"]
            }
            formatted_cities.append(formatted_city)
        return formatted_cities
    else:
        return {"error": "Failed to fetch cities"}

@app.route('/countries', methods=['GET'])
def get_countries():
    """
    Get countries from a hypothetical countries API.
    :return: List of countries in JSON format with country key, country code, and country name.
    """
    base_url = "https://api.example.com/countries"  # Replace with the actual API endpoint
    response = requests.get(base_url)
    if response.status_code == 200:
        countries = response.json()
        formatted_countries = []
        for country in countries:
            formatted_country = {
                "country_key": country["key"],
                "country_code": country["code"],
                "country_name": country["name"]
            }
            formatted_countries.append(formatted_country)
        return jsonify(formatted_countries)
    else:
        return jsonify({"error": "Failed to fetch countries"}), 500

@app.route('/weather_forecast_5days', methods=['GET'])
def get_5day_forecasts():
    location_key = request.args.get('locationKey')  # Get the location key from the URL request parameter
    endpoint = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}'

    params = {
        'apikey': API_KEY,
        'metric': 'true'  # Use 'true' to get temperatures in Celsius, 'false' for Fahrenheit
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        json_data = response.json()  # Convert the response to JSON
        return jsonify(json_data)
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Error fetching weather forecast: {e}'})

if __name__ == '__main__':
    app.run(debug=True)