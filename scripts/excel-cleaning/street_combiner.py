streets: list[str] = []

var: str = "any"

while var != "":
    var: str = input("Enter an address: ")
    var = var.strip()

    if var != "":
        var_split: list[str] = var.split()
        streets.append(" ".join(ele.strip() for ele in var_split))

print("\n".join(streets))