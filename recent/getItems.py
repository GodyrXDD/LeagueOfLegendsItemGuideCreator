import json
import re

# Define participant id to filter
participant_id_to_filter = 4  # change this to the ID you want

# Load your JSON file as a string
with open('data.json', 'r') as f:
    data_string = f.read()

# Remove leading zeros from numbers
corrected_data_string = re.sub(r':\s*0+(\d+)', r': \1', data_string)

# Parse the corrected string as JSON
data = json.loads(corrected_data_string)

# Function to recursively navigate through JSON object
def iterate_items(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                iterate_items(value)
            elif key == 'type' and value == 'ITEM_PURCHASED' and obj.get('participantId') == participant_id_to_filter:
                print({'itemId': obj['itemId'], 'timestamp': obj['timestamp']})  # print only item id and timestamp
            elif isinstance(value, int) and value == 0:
                obj[key] = None  # replace with None or any other value
    elif isinstance(obj, list):
        for item in obj:
            iterate_items(item)

# Iterate over the loaded data
iterate_items(data)
