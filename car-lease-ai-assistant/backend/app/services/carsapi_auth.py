import os
import time
import requests

CARS_API_BASE = "https://carapi.app/api"

CARS_API_TOKEN = os.environ.get("CARS_API_TOKEN")
CARS_API_SECRET = os.environ.get("CARS_API_SECRET")

_cached_jwt = None
_jwt_created_at = 0
_JWT_TTL = 20 * 60  # 20 minutes (safe default)


def get_carsapi_jwt() -> str:
    """
    Get cached CarsAPI JWT or generate a new one.
    CarsAPI /auth/v2 returns RAW JWT (plain text).
    """

    global _cached_jwt, _jwt_created_at

    now = time.time()

    # Reuse JWT if still valid
    if _cached_jwt and (now - _jwt_created_at) < _JWT_TTL:
        return _cached_jwt

    if not CARS_API_TOKEN or not CARS_API_SECRET:
        raise RuntimeError("CARS_API_TOKEN or CARS_API_SECRET not set")

    resp = requests.post(
        f"{CARS_API_BASE}/auth/login",
        json={
            "api_token": CARS_API_TOKEN,
            "api_secret": CARS_API_SECRET
        },
        headers={"Accept": "text/plain"},
        timeout=10
    )

    resp.raise_for_status()

    token = resp.text.strip()

    if not token:
        raise RuntimeError("CarsAPI returned empty JWT")

    _cached_jwt = token
    _jwt_created_at = now

    return token
