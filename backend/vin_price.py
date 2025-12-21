import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")

def get_vehicle_price(make, model, year):
    url = "https://vehicle-pricing-api.p.rapidapi.com/1837/get+vehicle+price+data"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "vehicle-pricing-api.p.rapidapi.com"
    }

    params = {
        "make": make,
        "model": model,
        "year": year
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()
