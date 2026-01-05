import httpx

async def get_vehicle_details(vin: str):
    """
    Fetches vehicle details from the free NHTSA API.
    """
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            data = response.json()
            
            # NHTSA returns a list of attributes. We need to filter for the ones we want.
            decoded = {}
            target_fields = ["Make", "Model", "Model Year", "Trim", "Body Class", "Engine HP"]
            
            for item in data.get("Results", []):
                if item["Variable"] in target_fields and item["Value"]:
                    decoded[item["Variable"]] = item["Value"]
            
            # If we didn't get a Make, the VIN might be invalid
            if not decoded.get("Make"):
                return None
                
            return decoded
            
        except Exception as e:
            print(f"VIN API Error: {e}")
            return None