import requests

def get_market_price(make, model, year, api_key):
    url = "https://vehicle-pricing-api.p.rapidapi.com/2775/get%2Bvehicle%2Bvalue"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "vehicle-pricing-api.p.rapidapi.com"
    }

    params = {
        "make": make,
        "model": model,
        "year": year
    }

    return requests.get(url, headers=headers, params=params).json()
