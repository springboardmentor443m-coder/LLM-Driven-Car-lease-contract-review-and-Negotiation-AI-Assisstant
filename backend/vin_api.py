import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VIN_API_KEY")
API_HOST = os.getenv("VIN_API_HOST")

VIN = "1GTG6CENOL1139305"  

url = "https://vehicle-pricing-api.p.rapidapi.com/vehicle"  

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST,
    "Accept": "application/json"
}

params = {
    "vin": VIN
}

response = requests.get(url, headers=headers, params=params)

print("Vehicle Data Retrieved Successfully")
print("Status Code:", response.status_code)

with open("../data/vin_api_response.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("VIN API response saved successfully")
