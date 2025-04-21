import unittest
import json
import os
import uuid
from tools.data_migrations import DataMigrator

class TestDataMigrations(unittest.TestCase):
    def setUp(self):
        self.migrator = DataMigrator()
        
    def test_migrate_0_1_to_1_0(self):
        # Create a v0.1 character data structure
        data = {
            "name": "Test Character",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4},
            "attributes": [],
            "defects": []
        }
        
        # Migrate the data
        migrated = self.migrator.migrate_character_data(data)
        
        # Check that required fields were added
        self.assertEqual(migrated["version"], "1.0")
        self.assertIn("background", migrated)
        self.assertIn("drama_points", migrated)
        self.assertIn("techniques", migrated)
        self.assertIn("templates", migrated)
        
    def test_migrate_0_2_to_1_0(self):
        # Create a v0.2 character data structure
        data = {
            "version": "0.2",
            "name": "Test Character",
            "attributes": [{"name": "Test Attribute"}],
            "defects": [{"name": "Test Defect"}]
        }
        
        # Migrate the data
        migrated = self.migrator.migrate_character_data(data)
        
        # Check that IDs were added
        self.assertEqual(migrated["version"], "1.0")
        self.assertTrue(all("id" in attr for attr in migrated["attributes"]))
        self.assertTrue(all("id" in defect for defect in migrated["defects"]))
        
    def test_migrate_0_3_to_1_0(self):
        # Create a v0.3 character data structure
        data = {
            "version": "0.3",
            "name": "Test Character"
        }
        
        # Migrate the data
        migrated = self.migrator.migrate_character_data(data)
        
        # Check that benchmark field was added
        self.assertEqual(migrated["version"], "1.0")
        self.assertIn("benchmark", migrated)
        self.assertIsNone(migrated["benchmark"])
        
    def test_no_migration_needed(self):
        # Create a v1.0 character data structure
        data = {
            "version": "1.0",
            "name": "Test Character",
            "background": {"origin": "", "faction": "", "goals": "", "personality": "", "history": ""},
            "drama_points": {"current": 3, "max": 5},
            "techniques": [],
            "templates": [],
            "benchmark": None
        }
        
        # Migrate the data
        migrated = self.migrator.migrate_character_data(data)
        
        # Check that no changes were made
        self.assertEqual(migrated, data)
        
    def test_invalid_version(self):
        # Create data with an invalid version
        data = {
            "version": "invalid",
            "name": "Test Character"
        }
        
        # Attempt to migrate the data
        with self.assertRaises(ValueError):
            self.migrator.migrate_character_data(data)

if __name__ == '__main__':
    unittest.main() 