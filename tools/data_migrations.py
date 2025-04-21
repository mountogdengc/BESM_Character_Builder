import json
from typing import Dict, Any
from datetime import datetime

class DataMigrator:
    def __init__(self):
        self.current_version = "1.0"
        self.migrations = {
            "0.1": self._migrate_0_1_to_1_0,
            "0.2": self._migrate_0_2_to_1_0,
            "0.3": self._migrate_0_3_to_1_0
        }
    
    def migrate_character_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate character data to the current version if needed"""
        if "version" not in data:
            # Assume oldest version if no version field
            data["version"] = "0.1"
        
        current_version = data["version"]
        if current_version == self.current_version:
            return data
            
        # Apply migrations in sequence
        while current_version != self.current_version:
            if current_version not in self.migrations:
                raise ValueError(f"No migration path from version {current_version} to {self.current_version}")
            
            data = self.migrations[current_version](data)
            current_version = data["version"]
            
        return data
    
    def _migrate_0_1_to_1_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.1 to 1.0"""
        # Add missing fields with default values
        if "background" not in data:
            data["background"] = {
                "origin": "",
                "faction": "",
                "goals": "",
                "personality": "",
                "history": ""
            }
            
        if "drama_points" not in data:
            data["drama_points"] = {
                "current": 3,
                "max": 5
            }
            
        if "techniques" not in data:
            data["techniques"] = []
            
        if "templates" not in data:
            data["templates"] = []
            
        # Update version
        data["version"] = "1.0"
        return data
    
    def _migrate_0_2_to_1_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.2 to 1.0"""
        # Add UUIDs to attributes and defects if missing
        import uuid
        
        for attr in data.get("attributes", []):
            if "id" not in attr:
                attr["id"] = str(uuid.uuid4())
                
        for defect in data.get("defects", []):
            if "id" not in defect:
                defect["id"] = str(uuid.uuid4())
                
        # Update version
        data["version"] = "1.0"
        return data
    
    def _migrate_0_3_to_1_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.3 to 1.0"""
        # Add benchmark field if missing
        if "benchmark" not in data:
            data["benchmark"] = None
            
        # Update version
        data["version"] = "1.0"
        return data 