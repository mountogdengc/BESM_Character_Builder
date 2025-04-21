import os
import json

def add_stat_mods_to_size_templates():
    """Add the stat_mods field to all size templates."""
    template_dir = os.path.join("data", "templates", "sizes")
    
    # Get all JSON files in the sizes directory
    size_files = [f for f in os.listdir(template_dir) if f.endswith('.json')]
    
    for size_file in size_files:
        file_path = os.path.join(template_dir, size_file)
        
        # Read the template file
        with open(file_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # Add stat_mods field if it doesn't exist
        if 'stat_mods' not in template_data:
            # Create a stat_mods field based on size rank
            size_rank = template_data.get('size_rank', 0)
            
            # Base stat modifiers on size rank
            # Smaller sizes (negative rank) typically have penalties to Body
            # Larger sizes (positive rank) typically have bonuses to Body
            body_mod = 0
            if size_rank < 0:
                # For very small sizes, apply penalties to Body
                if size_rank <= -5:
                    body_mod = -2
                else:
                    body_mod = -1
            elif size_rank > 0:
                # For large sizes, apply bonuses to Body
                if size_rank >= 5:
                    body_mod = 2
                else:
                    body_mod = 1
            
            # Create the stat_mods structure
            template_data['stat_mods'] = {
                "base": {
                    "Body": body_mod
                },
                "derived": {}
            }
            
            # Add derived stat modifiers based on existing modifiers if available
            if 'modifiers' in template_data:
                modifiers = template_data['modifiers']
                
                # Add armor rating modifier if applicable
                if 'armourEffect' in modifiers:
                    armor_effect = modifiers['armourEffect']
                    if '+' in armor_effect and 'damage' in armor_effect:
                        # This is a vulnerability, not a bonus to armor
                        template_data['stat_mods']['derived']['Armor Rating'] = -abs(int(armor_effect.split()[0].replace('+', '')))
                    elif '-' in armor_effect and 'damage' in armor_effect:
                        # This is a bonus to armor
                        template_data['stat_mods']['derived']['Armor Rating'] = abs(int(armor_effect.split()[0]))
            
            # Write the updated template back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
            
            print(f"Added stat_mods to {size_file}")
        else:
            print(f"stat_mods already exists in {size_file}")

if __name__ == "__main__":
    add_stat_mods_to_size_templates()
