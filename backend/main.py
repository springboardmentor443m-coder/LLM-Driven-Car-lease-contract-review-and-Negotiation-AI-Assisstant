from ai_analysis import analyze_contract
from vin_utils import is_valid_vin
from vin_price import get_vehicle_price

def read_contract_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    contract_path = r"C:\Users\rajal\Downloads\car_lease_ai\LLM-Driven-Car-lease-contract-review-and-Negotiation-AI-Assisstant\data\extracted_contract.txt"

    text = read_contract_text(contract_path)

    print("Contract text loaded successfully\n")

    result = analyze_contract(text)

    print("Contract Analysis Result")
    print("-" * 40)
    for key, value in result.items():
        print(f"{key}: {value}")

vin_number = input("\nEnter Vehicle VIN number: ").strip()

if is_valid_vin(vin_number):
    print("VIN is valid")
else:
    print("Invalid VIN number")


price_data = get_vehicle_price("Honda", "Accord", 2020)

print("Vehicle Market Price:")
print(price_data)



