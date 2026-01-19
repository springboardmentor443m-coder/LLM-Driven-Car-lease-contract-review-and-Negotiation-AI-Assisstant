import requests

NHTSA_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"

def verify_vin(vin: str):
    r = requests.get(NHTSA_URL.format(vin=vin)).json()

    vehicle = {}
    for item in r["Results"]:
        if item["Variable"] in ["Make", "Model", "Model Year", "Vehicle Type"]:
            vehicle[item["Variable"]] = item["Value"]

    valid = bool(vehicle.get("Make") and vehicle.get("Model"))
    return {
        "valid": valid,
        "vehicle": vehicle
    }
