import os
import json

def add_key_to_race_templates():
    """Add the key field to all race templates based on their filename."""
    template_dir = os.path.join("data", "templates", "races")
    
    # Get all JSON files in the races directory
    race_files = [f for f in os.listdir(template_dir) if f.endswith('.json')]
    
    for race_file in race_files:
        file_path = os.path.join(template_dir, race_file)
        
        # Extract key from filename (remove .json extension)
        key = race_file[:-5]
        
        # Read the template file
        with open(file_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # Add key field if it doesn't exist
        if 'key' not in template_data:
            template_data['key'] = key
            
            # Write the updated template back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
            
            print(f"Added key '{key}' to {race_file}")
        else:
            print(f"Key already exists in {race_file}")

if __name__ == "__main__":
    add_key_to_race_templates()
