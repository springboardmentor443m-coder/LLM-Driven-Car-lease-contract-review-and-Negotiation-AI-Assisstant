import requests
from typing import Optional
from app.services.carsapi_auth import get_carsapi_jwt

CARS_API_BASE = "https://carapi.app/api"


def get_msrp_from_carsapi(make: str, model: str, year: int) -> Optional[float]:
    """
    Fetch BASE MSRP (lowest trim price) from CarsAPI v2.
    """

    jwt = get_carsapi_jwt()

    headers = {
        "Authorization": f"Bearer {jwt}",
        "Accept": "application/json"
    }

    params = {
        "year": year,
        "make": make.lower(),
        "model": model.lower()
    }

    resp = requests.get(
        f"{CARS_API_BASE}/trims/v2",
        headers=headers,
        params=params,
        timeout=10
    )

    resp.raise_for_status()

    data = resp.json()
    trims = data.get("data", [])

    if not trims:
        return None

    msrps = [
        t["msrp"]
        for t in trims
        if t.get("msrp") is not None
    ]

    return float(min(msrps)) if msrps else None
