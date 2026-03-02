# Script used to find project IDs in the columns.
# This is used in case multiple PIDs are added in a column, each value has to be
# checked if it exists in ServiceNow prior to running the bulk.

pids: list[str] = []

pid: str = None

while pid != "":
    pid = input("Enter a project ID: ")

    if pid != "":
        pids.append(pid)

found_pid: set[str] = set()

for pid in pids:
    pid = pid.strip()

    if pid not in found_pid:
        found_pid.add(pid)

print("\n".join(found_pid))