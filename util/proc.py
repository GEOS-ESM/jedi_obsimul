#!/bin/python

# Read and process the input file
input_file = "input.txt"  # change to your filename

with open(input_file, "r") as f:
    lines = f.readlines()

# Process and print in the desired format
for line in lines:
    line = line.strip()
    if not line:
        continue
    name, url = line.split(maxsplit=1)
    print(f"{name}:")
    print(f"  local:     ./src/{name}")
    print(f"  remote:    {url}")
    print(f"  branch:    develop")
    print()
