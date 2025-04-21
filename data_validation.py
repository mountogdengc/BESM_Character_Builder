import json
import os
from jsonschema import validate, ValidationError
from typing import Dict, Any, Optional
from datetime import datetime

class DataValidator:
    def __init__(self):
        self.schemas = {}
        self.current_version = "1.0"
        self.load_schemas()
        
    def load_schemas(self):
        """Load JSON schemas from the docs/schemas directory"""
        schema_dir = os.path.join(os.path.dirname(__file__), "docs", "schemas")
        for schema_file in os.listdir(schema_dir):
            if schema_file.endswith("_schema.json"):
                with open(os.path.join(schema_dir, schema_file), 'r') as f:
                    schema_name = schema_file.replace("_schema.json", "")
                    self.schemas[schema_name] = json.load(f)
    
    def validate_character_data(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate character data against all relevant schemas"""
        try:
            # Check version
            if "version" not in data:
                data["version"] = self.current_version
            
            # Validate attributes
            for attr in data.get("attributes", []):
                validate(instance=attr, schema=self.schemas["attribute"])
            
            # Validate defects
            for defect in data.get("defects", []):
                validate(instance=defect, schema=self.schemas["defect"])
            
            # Validate items
            for item in data.get("items", []):
                validate(instance=item, schema=self.schemas["item"])
            
            return True, None
        except ValidationError as e:
            return False, str(e)
    
    def sanitize_character_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize character data to ensure it meets requirements"""
        sanitized = data.copy()
        
        # Ensure required fields exist
        required_fields = ["name", "player", "stats", "attributes", "defects"]
        for field in required_fields:
            if field not in sanitized:
                sanitized[field] = "" if field in ["name", "player"] else []
        
        # Sanitize stats
        if "stats" in sanitized:
            sanitized_stats = {}
            for stat in ["Body", "Mind", "Soul"]:
                try:
                    stat_value = sanitized["stats"].get(stat, 1)  # Default to 1 instead of 4
                    sanitized_stats[stat] = max(1, int(stat_value))
                except (ValueError, TypeError):
                    sanitized_stats[stat] = 1  # Set to 1 when conversion fails
            sanitized["stats"] = sanitized_stats
        
        # Sanitize attributes
        if "attributes" in sanitized:
            for attr in sanitized["attributes"]:
                attr["level"] = max(1, int(attr.get("level", 1)))
                if "cost_per_level" in attr:
                    attr["cost"] = attr["level"] * attr["cost_per_level"]
        
        # Sanitize defects
        if "defects" in sanitized:
            for defect in sanitized["defects"]:
                defect["rank"] = max(1, int(defect.get("rank", 1)))
        
        return sanitized
    
    def migrate_character_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate character data to the current version if needed"""
        version = data.get("version", "0.0")
        
        if version == self.current_version:
            return data
            
        migrated = data.copy()
        
        # Version 0.0 to 1.0 migration
        if version == "0.0":
            # Add version field
            migrated["version"] = "1.0"
            
            # Add missing fields
            if "benchmark" not in migrated:
                migrated["benchmark"] = None
            if "totalPoints" not in migrated:
                migrated["totalPoints"] = 0
            if "alternate_forms" not in migrated:
                migrated["alternate_forms"] = []
            if "metamorphosis" not in migrated:
                migrated["metamorphosis"] = []
            if "companions" not in migrated:
                migrated["companions"] = []
            if "minions" not in migrated:
                migrated["minions"] = []
        
        return migrated
    
    def create_backup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a backup of character data with timestamp"""
        backup = data.copy()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup["backup_timestamp"] = timestamp
        return backup 