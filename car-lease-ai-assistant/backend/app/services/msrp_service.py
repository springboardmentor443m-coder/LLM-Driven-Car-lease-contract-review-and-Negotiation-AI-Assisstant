def get_msrp(make: str, model: str, year: int) -> float:
    """
    Heuristic fallback MSRP estimation.
    Used only if CarsAPI fails.
    """

    base_prices = {
        ("HONDA", "Civic"): 22000,
        ("TOYOTA", "Corolla"): 21000,
        ("HYUNDAI", "Elantra"): 20000,
        ("FORD", "Focus"): 21000,
    }

    key = (make.upper(), model)

    base = base_prices.get(key, 25000)

    # Adjust for year (simple inflation adjustment)
    year_adjustment = max(0, year - 2015) * 400

    return float(base + year_adjustment)

