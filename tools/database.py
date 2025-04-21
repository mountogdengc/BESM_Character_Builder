import sqlite3
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def adapt_datetime(dt):
    """Convert datetime to ISO format string for SQLite storage"""
    return dt.isoformat()

def convert_datetime(s):
    """Convert ISO format string to datetime when reading from SQLite"""
    try:
        return datetime.fromisoformat(s.decode())
    except (ValueError, AttributeError):
        return None

# Register the converters with SQLite
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)

class DatabaseManager:
    def __init__(self, db_path: str = "characters.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._ensure_db_directory()
        self._connect()
        self._init_schema()
        
    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
    def _connect(self):
        """Establish connection to the database"""
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            # Enable foreign key support
            self.cursor.execute("PRAGMA foreign_keys = ON")
            # Use ISO format for timestamps
            self.cursor.execute("PRAGMA datetime_format = 'iso8601'")
        
    def _init_schema(self):
        """Initialize the database schema"""
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            );

            CREATE TRIGGER IF NOT EXISTS update_character_timestamp 
            AFTER UPDATE ON characters
            BEGIN
                UPDATE characters SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END;
        """)
        self.connection.commit()
        
    def save_character(self, character_data: Dict[str, Any], character_id: int = None) -> int:
        """Save a character to the database"""
        if not isinstance(character_data, dict):
            raise ValueError("Character data must be a dictionary")

        data_json = json.dumps(character_data, cls=DateTimeEncoder)
        name = character_data.get('name', '')
        version = character_data.get('version', 1)

        try:
            if character_id is not None:
                self.cursor.execute("""
                    UPDATE characters 
                    SET name = ?, version = ?, data = ? 
                    WHERE id = ?
                """, (name, version, data_json, character_id))
                if self.cursor.rowcount == 0:
                    raise ValueError(f"Character with id {character_id} not found")
                if not self._in_transaction():
                    self.connection.commit()
                return character_id
            else:
                # For new characters, always commit immediately to ensure they exist
                self.cursor.execute("""
                    INSERT INTO characters (name, version, data)
                    VALUES (?, ?, ?)
                """, (name, version, data_json))
                self.connection.commit()
                return self.cursor.lastrowid
        except sqlite3.Error as e:
            if not self._in_transaction():
                self.connection.rollback()
            raise ValueError(f"Database error: {str(e)}")
        
    def load_character(self, character_id: int) -> Optional[Dict[str, Any]]:
        """Load a character from the database"""
        try:
            self.cursor.execute("""
                SELECT id, name, version, data, created_at, updated_at
                FROM characters
                WHERE id = ?
            """, (character_id,))
            
            row = self.cursor.fetchone()
            if row:
                try:
                    character = json.loads(row['data'])
                    character['id'] = row['id']
                    character['created_at'] = row['created_at']
                    character['updated_at'] = row['updated_at']
                    return character
                except json.JSONDecodeError:
                    return None
            return None
        except sqlite3.Error:
            return None
        
    def list_characters(self) -> list:
        """List all characters in the database, ordered by most recent first"""
        self.cursor.execute("""
            SELECT id, name, version, created_at, updated_at
            FROM characters
            ORDER BY updated_at DESC, id DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]
        
    def delete_character(self, character_id: int):
        """Delete a character from the database"""
        self.cursor.execute("DELETE FROM characters WHERE id = ?", (character_id,))
        if self.cursor.rowcount == 0:
            raise ValueError(f"Character with id {character_id} not found")
        
    def create_backup(self, character_id: int) -> int:
        """Create a backup of a character"""
        character = self.load_character(character_id)
        if not character:
            raise ValueError(f"Character with id {character_id} not found")
            
        data_json = json.dumps(character, cls=DateTimeEncoder)
        self.cursor.execute("""
            INSERT INTO backups (character_id, data)
            VALUES (?, ?)
        """, (character_id, data_json))
        
        self.connection.commit()
        return self.cursor.lastrowid
        
    def restore_backup(self, backup_id: int) -> int:
        """Restore a character from a backup"""
        self.cursor.execute("""
            SELECT character_id, data
            FROM backups
            WHERE id = ?
        """, (backup_id,))
        
        row = self.cursor.fetchone()
        if not row:
            raise ValueError(f"Backup with id {backup_id} not found")
            
        character_data = json.loads(row['data'])
        character_id = row['character_id']
        self.save_character(character_data, character_id)
        return character_id
        
    def list_backups(self, character_id: int = None) -> list:
        """List all backups for a character or all characters if no specific character is provided"""
        query = """
            SELECT b.id, b.character_id, b.created_at, c.name as character_name
            FROM backups b
            JOIN characters c ON b.character_id = c.id
        """
        params = tuple()
        if character_id is not None:
            query += " WHERE b.character_id = ?"
            params = (character_id,)
        query += " ORDER BY b.created_at DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
        
    def close(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def _in_transaction(self):
        """Check if we're currently in a transaction"""
        if not self.connection:
            return False
        try:
            return bool(self.connection.in_transaction)
        except sqlite3.Error:
            return False
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def begin_transaction(self):
        """Begin a new transaction"""
        if not self.connection:
            self._connect()
        if not self._in_transaction():
            self.cursor.execute("BEGIN")
            
    def commit_transaction(self):
        """Commit the current transaction"""
        if self.connection and self._in_transaction():
            self.connection.commit()
            
    def rollback_transaction(self):
        """Rollback the current transaction"""
        if self.connection and self._in_transaction():
            self.connection.rollback() 