# Weather Tool

This is a simple Flask web application that allows users to look up the current weather by US zip code using the OpenWeatherMap API.



## Features

The overall intention is to lookup weather by zip code.
- The tool displays:
  - City
  - Current temperature (°F or °C)
  - Projected high & low temperatures
  - Weather description (e.g., cloudy, rainy)
- Error handling:
  - Invalid or empty zip codes
  - Zip codes not found in OpenWeatherMap
  - API timeouts or other network issues
- Uses Flask and Jinja2 templates for rendering HTML. Uses caching for repeated requests for the same zip code within 10 minutes to reduce API calls.


## Prerequisites

- Python 3.7+
- `pip`

## Setup

1. **Clone this repository**

```bash
git clone git@github.com:catherineeevans/weather-tool.git
cd weather-tool
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Get an OpenWeatherMap API key**
- Sign up at OpenWeatherMap to get an API key. 

- Set up your API key securely with a .env file in the project root. 

- Add your OpenWeatherMap API key inside the file:

```bash
OPENWEATHER_API_KEY=your_key
```

## Use the tool 
1. **Run the app**
```bash
python app.py
```
Use the local web address provided by Flask to access the tool in your browser

## Usage
- Enter a valid 5-digit US zip code in the form.
- Click Get Weather.
- The app will show the current weather information.
- If the zip is invalid or the API fails, an error message will appear.

## Running unit tests
This project's unit tests use Python's unittest module. 

To run all tests: 
```bash
python -m unittest discover -v
```