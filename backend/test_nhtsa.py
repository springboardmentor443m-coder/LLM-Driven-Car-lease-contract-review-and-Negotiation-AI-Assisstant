import requests
import json

# 1. Immediate print to prove the script is actually running
print("\n" + "="*50)
print("🚀 STARTING NHTSA API DIAGNOSTIC TEST")
print("="*50)

def run_test(vin):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    print(f"📡 Sending request to: {url}")
    
    try:
        # 2. Use a standard GET request with a 15-second timeout
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            print("✅ CONNECTION SUCCESSFUL: Received 200 OK")
            data = response.json()
            results = data.get("Results", [])
            
            # Extract key fields to verify data is flowing
            specs = {item['Variable']: item['Value'] for item in results 
                     if item['Variable'] in ["Make", "Model", "Model Year", "Body Class"]}
            
            print("\n📦 EXTRACTED VEHICLE DATA:")
            print(json.dumps(specs, indent=4))
            
            if specs.get("Make"):
                print("\n🎉 SUCCESS: NHTSA API is working and returning specs!")
            else:
                print("\n⚠️  WARNING: API connected, but returned empty values for this VIN.")
        else:
            print(f"❌ API ERROR: Server returned status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ SCRIPT CRASHED: {str(e)}")

# 3. This block MUST be at the very bottom to trigger execution
if __name__ == "__main__":
    # Testing with a known valid 2018 Toyota Camry VIN
    run_test("4T1B11HK5JU000001")
    print("="*50)
    print("🏁 TEST FINISHED")