import requests


def get_vehicle_specs(vin, api_key=None):
    """
    Fetch vehicle details using NHTSA VIN decoder.
    This function is defensive and will NEVER crash.
    """

    if not vin:
        return {
            "make": "Unknown",
            "model": "Unknown",
            "year": "Unknown"
        }

    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
        response = requests.get(url, timeout=10).json()

        results = response.get("Results", [])

        if not results:
            raise ValueError("No Results from NHTSA API")

        result = results[0]

        return {
            "make": result.get("Make", "Unknown"),
            "model": result.get("Model", "Unknown"),
            "year": result.get("ModelYear", "Unknown")
        }

    except Exception as e:
        # Fail safely — NEVER crash the app
        return {
            "make": "Unknown",
            "model": "Unknown",
            "year": "Unknown"
        }
