import pytest
from data_validation import DataValidator

def test_validate_character_data():
    validator = DataValidator()
    
    # Test valid data
    valid_data = {
        "name": "Test Character",
        "player": "Test Player",
        "stats": {"Body": 4, "Mind": 4, "Soul": 4},
        "attributes": [{"name": "Test Attribute", "key": "test", "level": 1}],
        "defects": [{"name": "Test Defect", "key": "test", "rank": 1}],
        "version": "1.0"
    }
    is_valid, error = validator.validate_character_data(valid_data)
    assert is_valid
    assert error is None
    
    # Test invalid data
    invalid_data = {
        "name": "Test Character",
        "player": "Test Player",
        "stats": {"Body": 0, "Mind": -1, "Soul": "invalid"},  # Invalid stats
        "attributes": [{"name": "Test Attribute"}],  # Missing required fields
        "defects": [{"name": "Test Defect"}],  # Missing required fields
        "version": "1.0"
    }
    is_valid, error = validator.validate_character_data(invalid_data)
    assert not is_valid
    assert error is not None

def test_sanitize_character_data():
    validator = DataValidator()
    
    # Test data with missing fields
    incomplete_data = {
        "name": "Test Character",
        "stats": {"Body": 0, "Mind": -1, "Soul": "invalid"}
    }
    sanitized = validator.sanitize_character_data(incomplete_data)
    
    # Check required fields were added
    assert "player" in sanitized
    assert "attributes" in sanitized
    assert "defects" in sanitized
    
    # Check stats were sanitized
    assert sanitized["stats"]["Body"] == 1
    assert sanitized["stats"]["Mind"] == 1
    assert sanitized["stats"]["Soul"] == 1

def test_migrate_character_data():
    validator = DataValidator()
    
    # Test migration from version 0.0
    old_data = {
        "name": "Test Character",
        "player": "Test Player",
        "stats": {"Body": 4, "Mind": 4, "Soul": 4},
        "attributes": [],
        "defects": [],
        "version": "0.0"
    }
    migrated = validator.migrate_character_data(old_data)
    
    # Check new fields were added
    assert migrated["version"] == "1.0"
    assert "benchmark" in migrated
    assert "totalPoints" in migrated
    assert "alternate_forms" in migrated
    assert "metamorphosis" in migrated
    assert "companions" in migrated
    assert "minions" in migrated

def test_create_backup():
    validator = DataValidator()
    
    test_data = {
        "name": "Test Character",
        "version": "1.0"
    }
    backup = validator.create_backup(test_data)
    
    assert "backup_timestamp" in backup
    assert backup["name"] == test_data["name"]
    assert backup["version"] == test_data["version"] 