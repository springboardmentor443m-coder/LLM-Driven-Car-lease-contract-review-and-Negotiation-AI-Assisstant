import os
import requests
from datetime import datetime
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

@lru_cache(maxsize=100)
def get_cached_market_price(vin, mileage, year):
    # This ensures we don't call the API twice for the same car/mileage combo
    return estimate_market_price(vin=vin, mileage=mileage, year=year)

def estimate_market_price(vin=None, mileage=15000, year=None):
    """
    Primary: RapidAPI Vehicle Pricing (Verified Working)
    Fallback: Heuristic Math
    """
    rapid_key = os.getenv("RAPID_API_KEY")
    url = "https://vehicle-pricing-api.p.rapidapi.com/1837/get%2Bvehicle%2Bprice%2Bdata"
    
    if rapid_key and vin:
        querystring = {"vin": vin, "mileage": str(mileage)}
        headers = {
            "x-rapidapi-key": rapid_key,
            "x-rapidapi-host": "vehicle-pricing-api.p.rapidapi.com"
        }
        
        try:
            print(f"📡 Requesting Market Value for VIN: {vin} at {mileage} miles...")
            resp = requests.get(url, headers=headers, params=querystring, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                # Accessing the specific nested 'prices' key from your successful test
                prices = data.get("data", {}).get("prices", {})
                avg_price = prices.get("average")
                
                if avg_price:
                    print(f"✅ API Success: ${avg_price}")
                    return float(avg_price)
            else:
                print(f"⚠️ RapidAPI returned {resp.status_code}: {resp.text}")
                
        except Exception as e:
            print(f"❌ RapidAPI Connection Error: {e}")

    # Fallback to Heuristic if API fails (using improved math for 2026)
    print("⚠️ Using Heuristic Fallback")
    model_year = int(year) if str(year).isdigit() else 2020
    current_year = 2026 # Updated for your current context
    age = max(0, current_year - model_year)
    
    # Using $35k as a more realistic starting base for modern cars
    base = 35000.0 
    # Gentler depreciation (12% annually)
    estimate = base * (0.88 ** age)
    return round(estimate, 2)