class AppState:
    raw_text = ""
    summary = ""
    vin = ""
    vehicle_specs = {}
    recalls = ""
    market_price = {}

    deal_analysis = {}
    resale_5yr = ""

    vectorstore = None

state = AppState()
