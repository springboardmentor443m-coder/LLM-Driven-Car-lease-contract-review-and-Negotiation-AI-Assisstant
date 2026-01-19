import requests


def decode_vin(vin):
    """
    Decode VIN using official NHTSA API
    Returns a dictionary with vehicle details
    """
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        results = response.json().get("Results", [])
        if not results:
            return None

        return results[0]

    except Exception as e:
        print("VIN decoding error:", e)
        return None


# ✅ Optional: run this file directly for testing only
if __name__ == "__main__":
    vin = "1GTG6CENOL1139305"  # sample VIN
    vehicle_data = decode_vin(vin)

    if vehicle_data:
        print("VIN Decoded Successfully\n")
        print("Make:", vehicle_data.get("Make"))
        print("Model:", vehicle_data.get("Model"))
        print("Model Year:", vehicle_data.get("ModelYear"))
        print("Body Class:", vehicle_data.get("BodyClass"))
        print("Fuel Type:", vehicle_data.get("FuelTypePrimary"))

        # Save output (optional)
        with open("../data/vin_decoded_data.txt", "w", encoding="utf-8") as f:
            for key, value in vehicle_data.items():
                f.write(f"{key}: {value}\n")

        print("\nVIN decoded data saved successfully")
    else:
        print("Failed to decode VIN")
