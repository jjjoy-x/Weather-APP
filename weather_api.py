import requests
from config import WEATHER_API_KEY

def search_locations(query, limit=5):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit={limit}&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def get_weather_by_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        try:
            return {"error": response.json().get("message", "Unknown error")}
        except:
            return {"error": "Failed to fetch weather data."}

def get_weather_forecast(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        try:
            return {"error": response.json().get("message", "Unknown error")}
        except:
            return {"error": "Failed to fetch forecast."}
        
def get_hourly_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Unable to fetch hourly forecast"}
