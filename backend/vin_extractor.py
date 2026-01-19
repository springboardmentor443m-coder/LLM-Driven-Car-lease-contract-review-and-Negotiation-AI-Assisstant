import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

contract_path = os.path.join(BASE_DIR, "..", "data", "extracted_contract.txt")

vin_output_path = os.path.join(BASE_DIR, "..", "data", "extracted_vin.txt")

with open(contract_path, "r", encoding="utf-8") as f:
    text = f.read()

vin_pattern = r"\b[A-HJ-NPR-Z0-9]{17}\b"
vin_match = re.search(vin_pattern, text)

if vin_match:
    vin = vin_match.group()
    print("VIN found:", vin)

    with open(vin_output_path, "w", encoding="utf-8") as f:
        f.write(vin)

    print("VIN saved to extracted_vin.txt")

else:
    print("VIN not found in contract")

