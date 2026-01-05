import httpx
import random

# --- CONFIGURATION ---
# Get a free key from https://rapidapi.com/category/Automotive if you want real data
RAPID_API_KEY = "RAPIDAPI_KEY" 
USE_MOCK_DATA = False # Set to False if you have a real API key

async def get_vehicle_valuation(vin: str):
    """
    Fetches official NHTSA data and Market Value.
    Falls back to mock data if APIs fail or are disabled.
    """
    vehicle_data = {"year": 2024, "make": "Unknown", "model": "Vehicle"}
    market_price = 30000  # Default fallback

    # 1. Fetch Basic Details (NHTSA is free and reliable)
    try:
        async with httpx.AsyncClient() as client:
            nhtsa_resp = await client.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json")
            if nhtsa_resp.status_code == 200:
                results = nhtsa_resp.json()['Results'][0]
                vehicle_data = {
                    "year": int(results.get('ModelYear', 2024) or 2024),
                    "make": results.get('Make', "Unknown"),
                    "model": results.get('Model', "Unknown"),
                    "trim": results.get('Trim', "Base"),
                    "vin": vin
                }
    except Exception as e:
        print(f"NHTSA Error: {e}")

    # 2. Fetch Market Price (Real or Mock)
    if USE_MOCK_DATA:
        # Generate a realistic "Market Price" around $28k - $45k for the demo
        market_price = random.randint(28000, 45000)
    else:
        # Real API Logic (requires paid key usually)
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "X-RapidAPI-Key": RAPID_API_KEY,
                    "X-RapidAPI-Host": "vehicle-market-value.p.rapidapi.com"
                }
                resp = await client.get("https://vehicle-market-value.p.rapidapi.com/vmv", 
                                      headers=headers, params={"vin": vin})
                if resp.status_code == 200:
                    market_price = resp.json().get('average_market_price', 30000)
        except Exception as e:
            print(f"Pricing API Error: {e}")

    return vehicle_data, market_price

def calculate_score(contract_price, market_price, money_factor):
    """
    Returns the score object for your frontend.
    """
    score = 100
    reasons = []
    
    # Logic: Price Comparison
    if contract_price > market_price:
        diff_percent = ((contract_price - market_price) / market_price) * 100
        penalty = int(diff_percent * 2) # Lose 2 points for every 1% over
        score -= penalty
        reasons.append(f"Dealer Price is {diff_percent:.1f}% higher than Market Value.")
    else:
        reasons.append("Deal Price is below Market Value (Good Deal).")

    # Logic: Money Factor (Interest)
    # Convert string to float safely
    try:
        mf = float(money_factor)
    except:
        mf = 0.0025 # Default if missing
        
    if mf > 0.0030:
        score -= 15
        reasons.append("High Rent Charge (Money Factor > 0.0030).")
    
    # Final cleanup
    final_score = max(10, min(100, int(score)))
    rating = "Excellent" if final_score > 85 else "Fair" if final_score > 60 else "Bad"
    
    return {
        "score": final_score,
        "rating": rating,
        "reasons": reasons
    }