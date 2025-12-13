import requests

NHTSA_DECODE = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{}?format=json"

def lookup_vin(vin):
    resp = requests.get(NHTSA_DECODE.format(vin))
    if resp.status_code != 200:
        return {"error": "NHTSA lookup failed", "status_code": resp.status_code}
    data = resp.json()
    results = data.get("Results", [])
    return results[0] if results else {}
