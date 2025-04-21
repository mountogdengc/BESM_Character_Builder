import os
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path
import logging
import uuid

class BackupManager:
    def __init__(self, app):
        self.app = app
        self.backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backups")
        self.ensure_backup_dir()
        self.setup_logging()

    def setup_logging(self):
        """Set up logging for backup operations"""
        log_dir = os.path.join(self.backup_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "backup.log")
        print(f"Setting up logging to: {log_file}")
        
        # Create a logger specific to this instance
        self.logger = logging.getLogger('backup_manager')
        self.logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create a file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(file_handler)
        
        # Log initialization
        self.logger.info("Backup manager initialized")
        print(f"Logging setup complete at {log_file}")

    def ensure_backup_dir(self):
        """Ensure the backup directory exists"""
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, character_data, manual=False):
        """Create a backup of character data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_type = "manual" if manual else "auto"
            # Add a unique identifier to ensure unique filenames
            unique_id = str(uuid.uuid4())[:8]
            filename = f"character_backup_{backup_type}_{timestamp}_{unique_id}.json"
            backup_path = os.path.join(self.backup_dir, filename)
            
            # Create backup file
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, indent=4)
            
            # Calculate checksum
            checksum = self.calculate_checksum(backup_path)
            
            # Create metadata
            metadata = {
                "filename": filename,
                "timestamp": timestamp,
                "type": backup_type,
                "checksum": checksum,
                "character_name": character_data.get("name", "Unnamed Character")
            }
            
            # Save metadata
            self.save_backup_metadata(metadata)
            
            self.logger.info(f"Created {backup_type} backup: {filename}")
            print(f"Created backup at: {backup_path}")
            return True, backup_path, None
            
        except Exception as e:
            error_msg = f"Failed to create backup: {str(e)}"
            self.logger.error(error_msg)
            print(f"Backup creation failed: {error_msg}")
            return False, None, error_msg

    def calculate_checksum(self, file_path):
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def save_backup_metadata(self, metadata):
        """Save backup metadata to history file"""
        history_file = os.path.join(self.backup_dir, "backup_history.json")
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
                
            history.append(metadata)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4)
                
        except Exception as e:
            self.logger.error(f"Failed to save backup metadata: {str(e)}")

    def get_backup_history(self):
        """Get list of all backups with metadata"""
        history_file = os.path.join(self.backup_dir, "backup_history.json")
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Failed to load backup history: {str(e)}")
            return []

    def verify_backup(self, backup_path):
        """Verify a backup file's integrity
        
        Args:
            backup_path (str): Path to the backup file
            
        Returns:
            tuple: (success bool, error_message str)
        """
        try:
            # Get expected checksum from metadata
            history = self.get_backup_history()
            filename = os.path.basename(backup_path)
            
            backup_meta = next((b for b in history if b["filename"] == filename), None)
            if not backup_meta:
                return False, "Backup not found in history"
                
            # Calculate current checksum
            current_checksum = self.calculate_checksum(backup_path)
            
            # Compare checksums
            if current_checksum != backup_meta["checksum"]:
                return False, "Checksum verification failed"
                
            # Verify JSON structure
            with open(backup_path, 'r', encoding='utf-8') as f:
                json.load(f)  # Will raise JSONDecodeError if invalid
                
            return True, None
            
        except Exception as e:
            return False, f"Verification failed: {str(e)}"

    def restore_backup(self, backup_path):
        """Restore character data from a backup
        
        Args:
            backup_path (str): Path to the backup file
            
        Returns:
            tuple: (success bool, character_data dict, error_message str)
        """
        try:
            # Verify backup first
            success, error = self.verify_backup(backup_path)
            if not success:
                return False, None, error
                
            # Load backup data
            with open(backup_path, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            self.logger.info(f"Restored backup: {os.path.basename(backup_path)}")
            return True, character_data, None
            
        except Exception as e:
            error_msg = f"Failed to restore backup: {str(e)}"
            self.logger.error(error_msg)
            return False, None, error_msg

    def cleanup_old_backups(self, max_backups=10):
        """Remove old backups to prevent disk space issues
        
        Args:
            max_backups (int): Maximum number of backups to keep
        """
        try:
            history = self.get_backup_history()
            print(f"Current history count: {len(history)}")
            if len(history) <= max_backups:
                print("No cleanup needed")
                return
                
            # Sort backups by timestamp (newest first)
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            print(f"Sorted history: {[b['filename'] for b in history]}")
            
            # Get list of files to keep
            files_to_keep = {b["filename"] for b in history[:max_backups]}
            print(f"Files to keep: {files_to_keep}")
            
            # Remove excess backups
            for backup in history[max_backups:]:
                backup_path = os.path.join(self.backup_dir, backup["filename"])
                print(f"Removing backup: {backup_path}")
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    self.logger.info(f"Removed old backup: {backup['filename']}")
                else:
                    print(f"Warning: Backup file not found: {backup_path}")
            
            # Update history file with only the kept backups
            history_file = os.path.join(self.backup_dir, "backup_history.json")
            print(f"Updating history file: {history_file}")
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history[:max_backups], f, indent=4)
            
            # Verify cleanup
            remaining_files = [f for f in os.listdir(self.backup_dir) 
                             if f.startswith("character_backup_") and f.endswith(".json")]
            print(f"Remaining backup files: {remaining_files}")
            
            # Verify all remaining files are in the history
            remaining_set = set(remaining_files)
            if not remaining_set.issubset(files_to_keep):
                extra_files = remaining_set - files_to_keep
                error_msg = f"Cleanup failed: Found extra files {extra_files}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            if len(remaining_files) > max_backups:
                error_msg = f"Cleanup failed: {len(remaining_files)} files remain, expected <= {max_backups}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {str(e)}")
            print(f"Cleanup error: {str(e)}")
            raise  # Re-raise the exception to fail the test 