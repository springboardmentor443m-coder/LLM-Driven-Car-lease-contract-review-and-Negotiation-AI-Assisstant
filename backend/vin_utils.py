import re

def is_valid_vin(vin):
    """
    VIN must be exactly 17 characters
    Letters I, O, Q are not allowed
    """
    vin = vin.upper()

    if len(vin) != 17:
        return False

    if re.search(r"[IOQ]", vin):
        return False

    if not re.match(r"^[A-HJ-NPR-Z0-9]{17}$", vin):
        return False

    return True
