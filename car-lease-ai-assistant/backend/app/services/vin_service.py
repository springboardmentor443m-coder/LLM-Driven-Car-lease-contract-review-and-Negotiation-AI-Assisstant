import re
import requests
import socket
from typing import Optional
socket.setdefaulttimeout(5)
requests.packages.urllib3.util.connection.HAS_IPV6 = False
NHTSA_BASE = "https://vpic.nhtsa.dot.gov/api/vehicles"


def extract_vin(text: str) -> Optional[str]:
    """
    Extract a valid 17-character VIN from text.
    """
    vin_pattern = r"\b[A-HJ-NPR-Z0-9]{17}\b"
    matches = re.findall(vin_pattern, text.upper())
    return matches[0] if matches else None


def decode_vin(vin: str) -> dict:
    """
    Decode VIN using NHTSA API.
    Returns empty dict on failure.
    """
    try:
        url = f"{NHTSA_BASE}/DecodeVin/{vin}?format=json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        results = resp.json().get("Results", [])
        data = {}

        for item in results:
            if item["Variable"] in [
                "Make",
                "Model",
                "Model Year",
                "Body Class",
                "Vehicle Type"
            ]:
                data[item["Variable"]] = item["Value"]

        return data

    except Exception as e:
        print(f"[VIN DECODE ERROR] {e}")
        return {}


def get_recalls(vin: str) -> list:
    """
    Fetch recall info using NHTSA API.
    Returns empty list on failure.
    """
    try:
        url = f"{NHTSA_BASE}/recalls/recallsByVehicle?vin={vin}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        return resp.json().get("results", [])

    except Exception as e:
        print(f"[RECALL FETCH ERROR] {e}")
        return []
