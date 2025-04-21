import unittest
import os
import json
from tools.data_access import DataAccess, DataAccessError, TransactionError
from datetime import datetime

class TestDataAccess(unittest.TestCase):
    def setUp(self):
        # Use a temporary database for testing
        self.db_path = "test_characters.db"
        # Remove any existing test database
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass  # File might be locked, will be overwritten
        self.data_access = DataAccess(self.db_path)
        
    def tearDown(self):
        # Clean up the test database
        try:
            self.data_access.close()  # Ensure connection is closed
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except PermissionError:
            pass  # Best effort cleanup
            
    def test_create_and_get_character(self):
        # Create test character data
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        
        # Create character
        character_id = self.data_access.create_character(character_data)
        self.assertIsNotNone(character_id)
        
        # Get character
        loaded_data = self.data_access.get_character(character_id)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["name"], character_data["name"])
        self.assertEqual(loaded_data["version"], character_data["version"])
        self.assertEqual(loaded_data["stats"], character_data["stats"])
        
    def test_update_character(self):
        # Create initial character
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.data_access.create_character(character_data)
        
        # Update character
        character_data["name"] = "Updated Character"
        character_data["stats"]["Body"] = 5
        success = self.data_access.update_character(character_id, character_data)
        self.assertTrue(success)
        
        # Verify update
        loaded_data = self.data_access.get_character(character_id)
        self.assertEqual(loaded_data["name"], "Updated Character")
        self.assertEqual(loaded_data["stats"]["Body"], 5)
        
    def test_delete_character(self):
        # Create character
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.data_access.create_character(character_data)
        
        # Delete character
        success = self.data_access.delete_character(character_id)
        self.assertTrue(success)
        
        # Verify deletion
        loaded_data = self.data_access.get_character(character_id)
        self.assertIsNone(loaded_data)
        
    def test_list_characters(self):
        # Create multiple characters
        for i in range(3):
            character_data = {
                "name": f"Test Character {i}",
                "version": "1.0",
                "stats": {"Body": 4, "Mind": 4, "Soul": 4}
            }
            self.data_access.create_character(character_data)
            
        # List characters
        characters = self.data_access.list_characters()
        self.assertEqual(len(characters), 3)
        self.assertEqual(characters[0]["name"], "Test Character 2")  # Most recent first
        
    def test_backup_and_restore(self):
        # Create character
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.data_access.create_character(character_data)
        
        # Create backup
        backup_id = self.data_access.create_backup(character_id)
        self.assertIsNotNone(backup_id)
        
        # Modify character
        character_data["name"] = "Modified Character"
        self.data_access.update_character(character_id, character_data)
        
        # Restore from backup
        restored_id = self.data_access.restore_backup(backup_id)
        self.assertEqual(restored_id, character_id)
        
        # Verify restore
        loaded_data = self.data_access.get_character(character_id)
        self.assertEqual(loaded_data["name"], "Test Character")
        
    def test_list_backups(self):
        # Create character and backups
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.data_access.create_character(character_data)
        
        # Create multiple backups
        backup_ids = []
        for _ in range(3):
            backup_id = self.data_access.create_backup(character_id)
            backup_ids.append(backup_id)
            
        # List all backups
        backups = self.data_access.list_backups()
        self.assertEqual(len(backups), 3)
        
        # List backups for specific character
        char_backups = self.data_access.list_backups(character_id)
        self.assertEqual(len(char_backups), 3)
        self.assertEqual(char_backups[0]["character_id"], character_id)
        
    def test_transaction_rollback(self):
        # Create initial character
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.data_access.create_character(character_data)
        
        # Verify initial state
        initial_data = self.data_access.get_character(character_id)
        self.assertEqual(initial_data["name"], "Test Character")
        
        # Try to update with valid data but force a rollback
        try:
            with self.data_access:
                # Update character with valid data
                update_data = character_data.copy()
                update_data["name"] = "Updated Character"
                self.data_access.update_character(character_id, update_data)
                # This should raise an exception and trigger rollback
                raise ValueError("Test error")
        except ValueError:
            pass
            
        # Clear any cached data
        self.data_access.clear_cache()
            
        # Verify character wasn't changed
        loaded_data = self.data_access.get_character(character_id)
        self.assertIsNotNone(loaded_data, "Character should still exist after rollback")
        self.assertEqual(loaded_data["name"], "Test Character", "Character name should not have changed after rollback")
        
    def test_caching(self):
        # Create character
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.data_access.create_character(character_data)
        
        # First load should cache
        loaded_data = self.data_access.get_character(character_id)
        self.assertEqual(loaded_data["name"], "Test Character")
        
        # Modify directly in database to test cache
        self.data_access.db.cursor.execute(
            "UPDATE characters SET data = ? WHERE id = ?",
            (json.dumps({"name": "Modified Character"}), character_id)
        )
        self.data_access.db.connection.commit()
        
        # Should get cached version
        cached_data = self.data_access.get_character(character_id)
        self.assertEqual(cached_data["name"], "Test Character")
        
        # Clear cache and reload
        self.data_access.clear_cache()
        fresh_data = self.data_access.get_character(character_id)
        self.assertEqual(fresh_data["name"], "Modified Character")
        
    def test_cache_invalidation(self):
        # Create character
        character_data = {
            "name": "Test Character",
            "version": "1.0",
            "stats": {"Body": 4, "Mind": 4, "Soul": 4}
        }
        character_id = self.data_access.create_character(character_data)
        
        # Load to cache
        self.data_access.get_character(character_id)
        
        # Update should invalidate cache
        character_data["name"] = "Updated Character"
        self.data_access.update_character(character_id, character_data)
        
        # Should get updated version
        loaded_data = self.data_access.get_character(character_id)
        self.assertEqual(loaded_data["name"], "Updated Character")
        
if __name__ == '__main__':
    unittest.main() 