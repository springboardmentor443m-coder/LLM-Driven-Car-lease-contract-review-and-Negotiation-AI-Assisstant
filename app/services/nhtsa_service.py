import requests

def get_recalls(make, model, year):
    url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}"
    data = requests.get(url).json().get("results", [])

    if not data:
        return "No recalls reported."

    text = ""
    for r in data:
        text += f"{r['Summary']} Remedy: {r['Remedy']}\n"

    return text
