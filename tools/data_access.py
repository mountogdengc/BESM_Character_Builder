import sqlite3
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from functools import wraps
import logging
from tools.database import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAccessError(Exception):
    """Base exception class for data access errors"""
    pass

class TransactionError(DataAccessError):
    """Exception raised for transaction-related errors"""
    pass

class CacheError(DataAccessError):
    """Exception raised for cache-related errors"""
    pass

class DataAccess:
    def __init__(self, db_path: str = "characters.db"):
        self.db_path = db_path
        self.db = None
        self.cache = {}
        self.transaction_depth = 0
        
    def _ensure_connection(self):
        """Ensure we have an active database connection"""
        if self.db is None:
            self.db = DatabaseManager(self.db_path)
        return self.db
        
    def close(self):
        """Close the database connection"""
        if self.db is not None:
            self.db.close()
            self.db = None
        self.cache.clear()
        
    def begin_transaction(self):
        """Begin a new transaction"""
        db = self._ensure_connection()
        if self.transaction_depth == 0:
            db.begin_transaction()
        self.transaction_depth += 1
        
    def commit_transaction(self):
        """Commit the current transaction"""
        if self.transaction_depth > 0:
            self.transaction_depth -= 1
            if self.transaction_depth == 0 and self.db is not None:
                try:
                    self.db.commit_transaction()
                finally:
                    self.cache.clear()
        
    def rollback_transaction(self):
        """Rollback the current transaction"""
        if self.transaction_depth > 0:
            self.transaction_depth = 0
            if self.db is not None:
                try:
                    self.db.rollback_transaction()
                finally:
                    self.cache.clear()
        
    def __enter__(self):
        self.begin_transaction()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback_transaction()
        else:
            try:
                self.commit_transaction()
            except:
                self.rollback_transaction()
                raise
        if self.transaction_depth == 0:
            self.close()
        
    def create_character(self, character_data: Dict[str, Any]) -> int:
        """Create a new character"""
        try:
            db = self._ensure_connection()
            character_id = db.save_character(character_data)
            self.cache.clear()  # Invalidate cache after modification
            return character_id
        except Exception as e:
            logger.error(f"Failed to create character: {str(e)}")
            raise DataAccessError(f"Failed to create character: {str(e)}")
            
    def update_character(self, character_id: int, character_data: Dict[str, Any]) -> bool:
        """Update an existing character"""
        try:
            db = self._ensure_connection()
            db.save_character(character_data, character_id)
            if character_id in self.cache:
                del self.cache[character_id]  # Invalidate cache
            return True
        except Exception as e:
            logger.error(f"Failed to update character {character_id}: {str(e)}")
            raise DataAccessError(f"Failed to update character {character_id}: {str(e)}")
            
    def get_character(self, character_id: int) -> Optional[Dict[str, Any]]:
        """Get a character by ID"""
        try:
            # Check cache first
            if character_id in self.cache and not self._in_transaction():
                return self.cache[character_id]
                
            db = self._ensure_connection()
            character = db.load_character(character_id)
            
            # Only cache if not in a transaction
            if character and not self._in_transaction():
                self.cache[character_id] = character
                
            return character
        except Exception as e:
            logger.error(f"Failed to get character {character_id}: {str(e)}")
            raise DataAccessError(f"Failed to get character {character_id}: {str(e)}")
            
    def _in_transaction(self):
        """Check if we're currently in a transaction"""
        return self.transaction_depth > 0
            
    def list_characters(self) -> List[Dict[str, Any]]:
        """List all characters"""
        try:
            db = self._ensure_connection()
            return db.list_characters()
        except Exception as e:
            logger.error(f"Failed to list characters: {str(e)}")
            raise DataAccessError(f"Failed to list characters: {str(e)}")
            
    def delete_character(self, character_id: int) -> bool:
        """Delete a character"""
        try:
            db = self._ensure_connection()
            db.delete_character(character_id)
            if character_id in self.cache:
                del self.cache[character_id]
            return True
        except Exception as e:
            logger.error(f"Failed to delete character {character_id}: {str(e)}")
            raise DataAccessError(f"Failed to delete character {character_id}: {str(e)}")
            
    def create_backup(self, character_id: int) -> int:
        """Create a backup of a character"""
        try:
            db = self._ensure_connection()
            return db.create_backup(character_id)
        except Exception as e:
            logger.error(f"Failed to create backup for character {character_id}: {str(e)}")
            raise DataAccessError(f"Failed to create backup for character {character_id}: {str(e)}")
            
    def restore_backup(self, backup_id: int) -> int:
        """Restore a character from a backup"""
        try:
            db = self._ensure_connection()
            character_id = db.restore_backup(backup_id)
            if character_id in self.cache:
                del self.cache[character_id]
            return character_id
        except Exception as e:
            logger.error(f"Failed to restore backup {backup_id}: {str(e)}")
            raise DataAccessError(f"Failed to restore backup {backup_id}: {str(e)}")
            
    def list_backups(self, character_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List backups for a character or all backups"""
        try:
            db = self._ensure_connection()
            return db.list_backups(character_id)
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            raise DataAccessError(f"Failed to list backups: {str(e)}")
            
    def clear_cache(self):
        """Clear the character cache"""
        self.cache.clear() 