import requests

NHTSA_BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended"


def decode_vin(vin: str) -> dict:
    """
    Decode VIN using official NHTSA API (FREE, Government-backed).
    """

    try:
        url = f"{NHTSA_BASE_URL}/{vin}?format=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("Results", [{}])[0]

        return {
            "make": results.get("Make"),
            "model": results.get("Model"),
            "model_year": results.get("ModelYear"),
            "body_class": results.get("BodyClass"),
            "fuel_type": results.get("FuelTypePrimary"),
            "manufacturer": results.get("Manufacturer"),
            "plant_country": results.get("PlantCountry"),
        }

    except Exception as e:
        return {
            "error": "NHTSA VIN decode failed",
            "details": str(e)
        }
