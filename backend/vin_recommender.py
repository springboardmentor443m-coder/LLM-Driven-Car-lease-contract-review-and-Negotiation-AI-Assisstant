from backend.vin_decoder import decode_vin


def generate_lease_recommendation(vin):
    vehicle = decode_vin(vin)

    if not vehicle:
        return "Unable to fetch vehicle details. Please check VIN."

    make = vehicle.get("Make", "Unknown")
    model = vehicle.get("Model", "Unknown")
    year = vehicle.get("ModelYear", "Unknown")
    body = vehicle.get("BodyClass", "")
    fuel = vehicle.get("FuelTypePrimary", "")

    recommendations = []

    # Logic-based suggestions
    if body.lower() in ["sport utility vehicle", "suv"]:
        recommendations.append(
            "SUV detected: Ensure higher mileage allowance and tire wear coverage."
        )

    if fuel.lower() in ["electric", "hybrid"]:
        recommendations.append(
            "Electric/Hybrid vehicle: Confirm battery warranty and charging clauses."
        )

    if year.isdigit() and int(year) < 2018:
        recommendations.append(
            "Older vehicle: Check maintenance responsibility and early termination clauses."
        )

    if not recommendations:
        recommendations.append(
            "Standard lease detected. Verify mileage limits and excess wear penalties."
        )

    summary = f"""
Vehicle Identified:
Make: {make}
Model: {model}
Year: {year}
Fuel Type: {fuel}

Lease Recommendations:
- """ + "\n- ".join(recommendations)

    return summary


# Test run
if __name__ == "__main__":
    test_vin = "1GTG6CEN0L1139305"
    print(generate_lease_recommendation(test_vin))
