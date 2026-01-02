import requests

CAR_API_BASE = "https://carapi.app/api"
CAR_API_KEY = "YOUR_CARAPI_KEY"  # env later

def get_vehicle_by_vin(vin: str) -> dict:
    url = f"{CAR_API_BASE}/vin/{vin}"
    params = {"apikey": CAR_API_KEY}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    return {
        "make": data.get("make"),
        "model": data.get("model"),
        "year": data.get("year"),
        "engine": data.get("engine"),
        "transmission": data.get("transmission"),
    }
