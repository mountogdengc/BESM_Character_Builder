import unittest
import os
import json
from tools.database import DatabaseManager
import time

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Use a temporary database for testing
        self.db_path = "test_characters.db"
        self.db = DatabaseManager(self.db_path)
        
    def tearDown(self):
        # Clean up the test database
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
    def test_save_and_load_character(self):
        # Create test character data
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        
        # Save character
        character_id = self.db.save_character(character_data)
        self.assertIsNotNone(character_id)
        
        # Load character
        loaded_data = self.db.load_character(character_id)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["name"], character_data["name"])
        self.assertEqual(loaded_data["version"], character_data["version"])
        self.assertEqual(loaded_data["stats"], character_data["stats"])
        self.assertEqual(loaded_data["id"], character_id)
        
    def test_update_character(self):
        # Create initial character
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.db.save_character(character_data)
        
        # Update character
        character_data["id"] = character_id
        character_data["name"] = "Updated Character"
        character_data["stats"]["Body"] = 5
        
        updated_id = self.db.save_character(character_data)
        self.assertEqual(updated_id, character_id)
        
        # Verify update
        loaded_data = self.db.load_character(character_id)
        self.assertEqual(loaded_data["name"], "Updated Character")
        self.assertEqual(loaded_data["stats"]["Body"], 5)
        
    def test_list_characters(self):
        # Create multiple characters
        for i in range(3):
            character_data = {
                "name": f"Test Character {i}",
                "version": "1.0",
                "stats": {"Body": 4, "Mind": 4, "Soul": 4}
            }
            print(f"Creating character {i}")
            character_id = self.db.save_character(character_data)
            print(f"Created character {i} with ID {character_id}")
            time.sleep(0.1)  # Add small delay to ensure different timestamps
            
        # List characters
        characters = self.db.list_characters()
        print("\nListed characters:")
        for char in characters:
            print(f"ID: {char['id']}, Name: {char['name']}, Updated: {char['updated_at']}")
            
        self.assertEqual(len(characters), 3)
        self.assertEqual(characters[0]["name"], "Test Character 2")  # Most recent first
        
    def test_backup_and_restore(self):
        # Create character
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.db.save_character(character_data)
        
        # Create backup
        backup_id = self.db.create_backup(character_id)
        self.assertIsNotNone(backup_id)
        
        # Modify character
        character_data["id"] = character_id
        character_data["name"] = "Modified Character"
        self.db.save_character(character_data)
        
        # Restore from backup
        restored_id = self.db.restore_backup(backup_id)
        self.assertEqual(restored_id, character_id)
        
        # Verify restore
        loaded_data = self.db.load_character(character_id)
        self.assertEqual(loaded_data["name"], "Test Character")
        
    def test_invalid_character_id(self):
        # Try to load non-existent character
        loaded_data = self.db.load_character(999)
        self.assertIsNone(loaded_data)
        
    def test_invalid_backup_id(self):
        # Try to restore non-existent backup
        with self.assertRaises(ValueError):
            self.db.restore_backup(999)
            
    def test_context_manager(self):
        # Test database manager as context manager
        with DatabaseManager(self.db_path) as db:
            character_data = {
                "name": "Test Character",
                "version": "1.0",
                "stats": {"Body": 4, "Mind": 4, "Soul": 4}
            }
            character_id = db.save_character(character_data)
            self.assertIsNotNone(character_id)
            
if __name__ == '__main__':
    unittest.main() 