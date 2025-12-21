import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")

def get_vehicle_details(vin):
    url = "https://carapi.app/api/vin/" + vin

    headers = {
        "X-RapidAPI-Key": API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": "Failed to fetch vehicle data",
            "status_code": response.status_code
        }


if __name__ == "__main__":
    test_vin = "1HGCM82633A004352"
    data = get_vehicle_details(test_vin)
    print(data)

