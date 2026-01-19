def analyze_lease(contract_data, vehicle):
    suggestions = []

    if contract_data["penalty_clause"] == "Present":
        suggestions.append("Penalty clause detected. Negotiate penalty terms.")

    if contract_data["mileage_limit"] != "Not found":
        suggestions.append("Check if mileage limit suits your driving needs.")

    if vehicle:
        year = vehicle.get("ModelYear")
        if year and year.isdigit() and int(year) < 2020:
            suggestions.append("Vehicle is an older model. Lease price can be negotiated.")

    if not suggestions:
        suggestions.append("Lease terms appear reasonable.")

    return suggestions
