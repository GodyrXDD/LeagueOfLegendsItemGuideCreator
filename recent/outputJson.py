import json

def print_json(data, indent=0):
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{' ' * indent}{key}:")
            print_json(value, indent + 2)
    elif isinstance(data, list):
        for item in data:
            print_json(item, indent)
    else:
        print(f"{' ' * indent}{data}")

# Load JSON from a file
with open('data.json') as file:
    data = json.load(file)

# Print the labeled hierarchical output
print_json(data)