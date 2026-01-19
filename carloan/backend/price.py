import requests
import os

VD_VIN_URL = "https://api.vehicledatabases.com/market-value/v2/{vin}"

def get_market_price_by_vin(vin: str):
    """
    Returns estimated market price using VIN.
    If API fails or key is missing, returns None.
    """

    api_key = os.getenv("VEHICLEDATABASES_API_KEY")

    # 1️⃣ If API key not provided
    if not api_key:
        print("Market price skipped: API key not found")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(
            VD_VIN_URL.format(vin=vin),
            headers=headers,
            timeout=10
        )

        # 2️⃣ API failed
        if response.status_code != 200:
            print("Market price API failed:", response.status_code)
            return None

        data = response.json()

        # 3️⃣ Extract price safely
        return data.get("price")

    except Exception as e:
        print("Market price exception:", e)
        return None
