import os
import requests
from dotenv import load_dotenv

load_dotenv()

def estimate_market_price(vin, mileage):
    """
    STRICT IMPLEMENTATION: Only VIN and Mileage as required by the API.
    """
    rapid_key = os.getenv("RAPID_API_KEY")
    url = "https://vehicle-pricing-api.p.rapidapi.com/1837/get%2Bvehicle%2Bprice%2Bdata"
    
    # The API only asked for these two
    querystring = {"vin": vin, "mileage": str(mileage)}
    
    headers = {
        "x-rapidapi-key": rapid_key,
        "x-rapidapi-host": "vehicle-pricing-api.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            # Extract only the average price we need for the fairness score
            return data.get("prices", {}).get("average", 0)
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        
    # If API fails, return a flat fallback so the app doesn't crash
    return 22000.0