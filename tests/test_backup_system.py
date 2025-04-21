import os
import json
import shutil
import pytest
import logging
from datetime import datetime
from pathlib import Path
from tools.backup_manager import BackupManager
import time

@pytest.fixture
def temp_backup_dir(tmp_path):
    """Create a temporary backup directory for testing"""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return backup_dir

@pytest.fixture
def temp_path(tmp_path):
    """Create a temporary directory for export testing"""
    return tmp_path

@pytest.fixture
def sample_character_data():
    """Create sample character data for testing"""
    return {
        "name": "Test Character",
        "player": "Test Player",
        "stats": {
            "Body": 4,
            "Mind": 4,
            "Soul": 4
        },
        "attributes": [],
        "defects": []
    }

@pytest.fixture
def backup_manager(temp_backup_dir, sample_character_data):
    """Create a BackupManager instance for testing"""
    class MockApp:
        def __init__(self):
            self.character_data = sample_character_data
    
    app = MockApp()
    manager = BackupManager(app)
    
    # Set the backup directory to the temporary directory
    manager.backup_dir = str(temp_backup_dir)
    
    # Ensure the logs directory exists
    log_dir = os.path.join(manager.backup_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Reconfigure logging to use the temporary directory
    manager.setup_logging()
    
    return manager

def test_backup_creation(backup_manager, sample_character_data):
    """Test creating a backup"""
    success, path, error = backup_manager.create_backup(sample_character_data, manual=True)
    
    assert success
    assert path is not None
    assert error is None
    assert os.path.exists(path)
    
    # Verify backup file contents
    with open(path, 'r') as f:
        saved_data = json.load(f)
    assert saved_data == sample_character_data

def test_backup_metadata(backup_manager, sample_character_data):
    """Test backup metadata creation and storage"""
    success, path, _ = backup_manager.create_backup(sample_character_data, manual=True)
    assert success
    
    # Get backup history
    history = backup_manager.get_backup_history()
    assert len(history) == 1
    
    backup_meta = history[0]
    assert backup_meta["character_name"] == sample_character_data["name"]
    assert backup_meta["type"] == "manual"
    assert "timestamp" in backup_meta
    assert "checksum" in backup_meta
    assert "filename" in backup_meta

def test_backup_verification(backup_manager, sample_character_data):
    """Test backup verification"""
    success, path, _ = backup_manager.create_backup(sample_character_data, manual=True)
    assert success
    
    # Verify the backup
    verify_success, error = backup_manager.verify_backup(path)
    assert verify_success
    assert error is None
    
    # Corrupt the backup file
    with open(path, 'w') as f:
        f.write("corrupted data")
    
    # Verify should fail
    verify_success, error = backup_manager.verify_backup(path)
    assert not verify_success
    assert error is not None

def test_backup_restore(backup_manager, sample_character_data):
    """Test backup restoration"""
    success, path, _ = backup_manager.create_backup(sample_character_data, manual=True)
    assert success
    
    # Restore the backup
    restore_success, restored_data, error = backup_manager.restore_backup(path)
    assert restore_success
    assert restored_data == sample_character_data
    assert error is None

def test_automatic_backup_cleanup(backup_manager, sample_character_data):
    """Test automatic cleanup of old backups"""
    # Create more backups than the limit
    max_backups = 5
    created_backups = []
    
    for i in range(max_backups + 2):
        # Add a small delay to ensure unique timestamps
        time.sleep(0.1)
        success, path, error = backup_manager.create_backup(sample_character_data, manual=True)
        assert success, f"Failed to create backup {i}: {error}"
        created_backups.append(path)
        print(f"Created backup {i+1}: {path}")
    
    # Get initial history
    initial_history = backup_manager.get_backup_history()
    print(f"Initial history count: {len(initial_history)}")
    print(f"Initial history files: {[b['filename'] for b in initial_history]}")
    
    # Run cleanup
    backup_manager.cleanup_old_backups(max_backups)
    
    # Get final history
    history = backup_manager.get_backup_history()
    print(f"Final history count: {len(history)}")
    print(f"Final history files: {[b['filename'] for b in history]}")
    assert len(history) <= max_backups, f"History contains {len(history)} entries, expected <= {max_backups}"
    
    # Verify files exist and match history
    for backup in history:
        path = os.path.join(backup_manager.backup_dir, backup["filename"])
        print(f"Checking backup file: {path}")
        assert os.path.exists(path), f"Backup file not found: {path}"
    
    # Verify no extra files exist
    backup_files = [f for f in os.listdir(backup_manager.backup_dir) 
                   if f.startswith("character_backup_") and f.endswith(".json")]
    print(f"Found backup files: {backup_files}")
    assert len(backup_files) <= max_backups, f"Found {len(backup_files)} backup files, expected <= {max_backups}"
    
    # Verify history matches actual files
    history_filenames = {b["filename"] for b in history}
    actual_filenames = set(backup_files)
    assert history_filenames == actual_filenames, "History and actual files don't match"

def test_backup_history_sorting(backup_manager, sample_character_data):
    """Test backup history sorting"""
    # Create multiple backups
    for i in range(3):
        backup_manager.create_backup(sample_character_data, manual=True)
    
    # Get history
    history = backup_manager.get_backup_history()
    
    # Verify sorting (newest first)
    timestamps = [b["timestamp"] for b in history]
    assert timestamps == sorted(timestamps, reverse=True)

def test_backup_error_handling(backup_manager):
    """Test error handling in backup operations"""
    # Test with invalid data
    success, path, error = backup_manager.create_backup(None)
    assert not success
    assert path is None
    assert error is not None
    
    # Test with invalid path
    verify_success, error = backup_manager.verify_backup("nonexistent_path")
    assert not verify_success
    assert error is not None
    
    # Test restore with invalid path
    restore_success, data, error = backup_manager.restore_backup("nonexistent_path")
    assert not restore_success
    assert data is None
    assert error is not None

def test_backup_logging(backup_manager, sample_character_data, temp_backup_dir):
    """Test backup logging functionality"""
    # Create a backup
    backup_manager.create_backup(sample_character_data, manual=True)
    
    # Check log file exists
    log_file = os.path.join(temp_backup_dir, "logs", "backup.log")
    print(f"Looking for log file at: {log_file}")
    print(f"Directory contents: {os.listdir(os.path.dirname(log_file))}")
    assert os.path.exists(log_file), f"Log file not found at {log_file}"
    
    # Check log content
    with open(log_file, 'r') as f:
        log_content = f.read()
    print(f"Log content: {log_content}")
    assert "Created" in log_content, "Log does not contain 'Created'"
    assert "backup" in log_content.lower(), "Log does not contain 'backup'"
    assert "manual" in log_content.lower(), "Log does not contain 'manual'"

def test_backup_export(backup_manager, sample_character_data, temp_path):
    """Test backup export functionality"""
    # Create a backup
    success, path, _ = backup_manager.create_backup(sample_character_data, manual=True)
    assert success
    
    # Export to new location
    export_path = os.path.join(temp_path, "exported_backup.json")
    shutil.copy2(path, export_path)
    
    # Verify exported file
    assert os.path.exists(export_path)
    with open(export_path, 'r') as f:
        exported_data = json.load(f)
    assert exported_data == sample_character_data

def test_backup_directory_creation(backup_manager):
    """Test backup directory creation"""
    # Backup directory should be created during initialization
    assert os.path.exists(backup_manager.backup_dir)
    
    # Logs directory should also be created
    logs_dir = os.path.join(backup_manager.backup_dir, "logs")
    assert os.path.exists(logs_dir) 