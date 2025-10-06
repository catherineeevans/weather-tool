from flask import Flask, render_template, request
import requests
import re
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)

api_key = os.getenv("OPENWEATHER_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENWEATHER_API_KEY in environment config")

cache = {}
cache_expiration = timedelta(minutes=10) 

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/weather", methods=["GET"])
def weather():
    try:
        zip_code, units, country_code = get_request_params()
        logging.info(f"Received zip code: {zip_code} with units={units}")

        if not re.match(r"^\d{5}$", zip_code): #5 digits 
            error_message = "Please enter a valid 5-digit US zip code."
            logging.warning(f"Invalid zip code entered: {zip_code}")
            return render_template("index.html", error=error_message)

        cache_key = f"{zip_code}_{units}"
        weather_info = get_cached_weather(cache_key)
        if weather_info:
            return render_template("weather.html", weather=weather_info, units=units)

        response = pull_weather_response(zip_code, country_code, units)
        if response is None:
            error_message = "Something went wrong while fetching the weather. Please try again later."
            logging.error(f"Request failed for zip: {zip_code}")
            return render_template("index.html", error=error_message)

        if response.status_code == 200:
            weather_info = parse_weather_data(response.json())
            logging.info(f"Successfully retrieved weather for {zip_code}")
            cache[cache_key] = (weather_info, datetime.now() + cache_expiration)
            return render_template("weather.html", weather=weather_info, units=units)
        elif response.status_code == 404:
            error_message = f"Weather information is not available for {zip_code}. Please try a different zip code."
            logging.warning(f"No data found for zip: {zip_code}")
            return render_template("index.html", error=error_message)
        else:
            error_message = "Something went wrong while pulling the weather. Please try again later."
            logging.error(f"Unexpected status code {response.status_code} for zip: {zip_code}")
            return render_template("index.html", error=error_message)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        error_message = "An unexpected error occurred. Please try again later."
        return render_template("index.html", error=error_message)

def get_request_params():
    zip_code = request.args.get("zip_code", "").strip()
    country_code = "us"
    units = request.args.get("units", "imperial")
    return zip_code, units, country_code

def get_cached_weather(cache_key):
    if cache_key in cache:
        cached_response, expiration = cache[cache_key]
        if datetime.now() < expiration:
            logging.info(f"Using cached weather for {cache_key}")
            return cached_response
        else:
            del cache[cache_key]  # remove expired cache
    return None

def pull_weather_response(zip_code, country_code, units):
    url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},{country_code}&units={units}&appid={api_key}"
    try:
        response = requests.get(url, timeout=5)
        logging.info(f"API request sent to OpenWeather for zip {zip_code}")
        return response
    except requests.Timeout:
        logging.error(f"Timeout while pulling weather for zip: {zip_code}")
        return None
    except requests.RequestException as e:
        logging.error(f"RequestException for zip {zip_code}: {e}")
        return None

def parse_weather_data(data):
    try:
        weather_descriptions = ", ".join([w["description"] for w in data["weather"]])
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "description": weather_descriptions
        }
    except (KeyError, TypeError) as e:
        logging.error(f"Error parsing weather data: {e}")
        raise

if __name__ == "__main__":
    app.run(debug=True, port=0)
