import os
import requests
from datetime import datetime

# API Endpoint
VD_VIN_URL = "https://api.vehicledatabases.com/market-value/v2/{vin}"

def estimate_market_price(vin=None, year=None, body="sedan"):
    # Must match the .env key name exactly
    vd_key = os.getenv("VEHICLE_DB_KEY")
    
    if vd_key and vin:
        # FIX 1: Use 'Subscription-Key' instead of 'x-AuthKey'
        headers = {
            'Subscription-Key': vd_key, 
            'Accept': 'application/json'
        }
        try:
            resp = requests.get(VD_VIN_URL.format(vin=vin), headers=headers, timeout=12)
            
            # If we get a 401 here, the key is still being rejected
            if resp.status_code == 200:
                data = resp.json()
                
                # FIX 2: Dynamic extraction to handle different API response shapes
                # First, check the most direct path
                direct_val = data.get("data", {}).get("market_value")
                if isinstance(direct_val, (int, float)):
                    return float(direct_val)

                # Fallback to your nested list logic if the direct path fails
                mv_data = data.get("data", {}).get("market_value", {}).get("market_value_data", [])
                if mv_data:
                    for entry in mv_data[0].get("market value", []):
                        if entry.get("Condition") == "Clean":
                            val = entry.get("Dealer Retail")
                            return float(str(val).replace("$","").replace(",",""))
            else:
                print(f"VehicleDatabases API Rejected Key: {resp.status_code} - {resp.text}")

        except Exception as e:
            print(f"VehicleDatabases Connection Error: {e}")

    # Fallback to Heuristic if API fails
    # This prevents the $10,200 loop by providing a more realistic Camry baseline
    model_year = int(year) if str(year).isdigit() else 2018
    age = max(0, datetime.now().year - model_year)
    
    # Standard base prices for common vehicles
    base = 25000.0 if "camry" in str(body).lower() else 30000.0
    estimate = base * (0.88 ** age) # Realistic 12% annual depreciation
    
    return round(estimate, 2)