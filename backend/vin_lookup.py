import requests

def lookup_vin(vin):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    res = requests.get(url).json()

    data = {
        "Make": "",
        "Model": "",
        "Year": "",
        "BodyClass": "",
        "FuelType": ""
    }

    for item in res.get("Results", []):
        if item["Variable"] == "Make":
            data["Make"] = item["Value"] or ""
        if item["Variable"] == "Model":
            data["Model"] = item["Value"] or ""
        if item["Variable"] == "Model Year":
            data["Year"] = item["Value"] or ""
        if item["Variable"] == "Body Class":
            data["BodyClass"] = item["Value"] or ""
        if item["Variable"] == "Fuel Type - Primary":
            data["FuelType"] = item["Value"] or ""

    return data