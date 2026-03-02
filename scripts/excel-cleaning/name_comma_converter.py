# Script used for converting first and last names into a full name. 
# The name format is expected to be [Last Name, First Name] with the comma being the
# delimiter. 
#
# It outputs the names into terminal.

names: list[str] = []

name: str = None

while name != "":
    name = input("Enter a list of names: ")

    if name != "":
        names.append(name)

full_names: list[str] = []
has_error: bool = False

for name in names:
    split_name: list[str] = name.split(",")

    if len(split_name) > 1:
        full_names.append(f"{split_name[-1].strip()} {split_name[0].strip()}")
    else:
        has_error = True

        print(f"{name} does not have a character ','")

if len(full_names) > 0 and not has_error:
    print("\n".join(full_names))
else:
    print("Correct the given input names")