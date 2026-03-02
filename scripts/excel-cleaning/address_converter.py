from pathlib import Path
import pandas as pd

# Converts an address into a csv. This is required due to it being divided
# into four cells, used for the main data source.
#
# This assumes the address format is as follows: STREET, CITY, STATE, POSTAL
# It splits by a delimiter, can be changed below.

DELIMITER: str = ","
ROOT_DIR: Path = Path(__file__).parent.parent

csv_data: dict[str, list[str]] = {
    "Street": [],
    "City": [],
    "State": [],
    "Postal": [],
}

addresses: list[str] = []
while True:
    data: list[str] = input("Enter an address: ")

    if data == "":
        break

    addresses.append(data)

has_error: bool = False

streets: list[str] = []
cities: list[str] = []
states: list[str] = []
postals: list[str] = []

for address in addresses:
    address_parts: list[str] = address.split(DELIMITER)

    address_parts = [val.strip() for val in address_parts]

    if len(address_parts) != 4:
        print(f"Address {address} has an incorrect format, requires needs correction")
        if not has_error: 
            has_error = True
        continue
    
    streets.append(address_parts[0])
    cities.append(address_parts[1])
    states.append(address_parts[2])
    postals.append(address_parts[-1])

csv_data["Street"] = streets
csv_data["City"] = cities
csv_data["State"] = states
csv_data["Postal"] = postals

if not has_error and len(addresses) > 0:
    df: pd.DataFrame = pd.DataFrame(csv_data)

    FILENAME: str = "output_address.xlsx"

    df.to_excel(ROOT_DIR / FILENAME, index=False)
    print(f"Created {FILENAME}")