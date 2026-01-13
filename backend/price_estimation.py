import requests
import os

def estimate_vehicle_price(vin, mileage):
    if not vin:
        return None

    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("RAPIDAPI_KEY not set")
        return None

    url = "https://vehicle-pricing-api.p.rapidapi.com/get-vehicle-pricing-data"

    querystring = {
        "vin": vin,
        "mileage": mileage or 50000
    }

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "vehicle-pricing-api.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()

        print("PRICE API RAW RESPONSE:", data)

        pricing = data.get("pricing", {})

        return {
            "below_market_price": pricing.get("belowMarket"),
            "average_market_price": pricing.get("averageMarket"),
            "above_market_price": pricing.get("aboveMarket"),
            "confidence": pricing.get("confidence")
        }

    except Exception as e:
        print("PRICE API ERROR:", e)
        return None