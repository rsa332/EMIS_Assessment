import os
import json
import pandas as pd
from collections import defaultdict

data_folder = "data"

# Initialize a dictionary to group data by resourceType
resource_data = defaultdict(list)


# Process each JSON file in the data folder
def extract_data():
    for filename in os.listdir(data_folder):
        if filename.endswith(".json"):
            filepath = os.path.join(data_folder, filename)
            with open(filepath, "r", encoding='utf-8') as file:
                try:
                    # Load JSON data
                    data = json.load(file)

                    # Group data by resourceType
                    for resource in data.get("entry", []):
                        resource_type = resource.get("resource", {}).get("resourceType")
                        if resource_type:
                            resource_data[resource_type].append(resource["resource"])
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in file {filename}: {e}")
        # Create DataFrames from the extracted data
    df_patient = pd.DataFrame(resource_data.get('Patient', []))
    df_condition = pd.DataFrame(resource_data.get('Condition', []))
    df_encounter = pd.DataFrame(resource_data.get('Encounter', []))

    return df_patient, df_condition, df_encounter