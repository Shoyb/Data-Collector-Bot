"""
Database management module for Data Collector Bot.
Handles all SQLite database operations.
"""
import sqlite3
from config import DATABASE_NAME
from typing import List, Optional, Tuple


class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, db_name: str = DATABASE_NAME):
        """Initialize database connection and create tables."""
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Create tables if they don't exist."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            saved_text TEXT
        )
        """)
        self.conn.commit()
    
    def save_user_data(self, user_id: int, text: str) -> bool:
        """
        Save user data to database.
        
        Args:
            user_id: Discord user ID
            text: Text to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute("""
            INSERT INTO user_data (user_id, saved_text)
            VALUES (?, ?)
            """, (user_id, text))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
    
    def get_user_data(self, user_id: int) -> Optional[str]:
        """
        Get saved data for a specific user.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Saved text or None if not found
        """
        try:
            self.cursor.execute(
                "SELECT saved_text FROM user_data WHERE user_id = ?", 
                (user_id,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting user data: {e}")
            return None
    
    def get_all_user_data(self) -> List[Tuple[int, str]]:
        """
        Get all saved user data.
        
        Returns:
            List of tuples (user_id, saved_text)
        """
        try:
            self.cursor.execute("SELECT user_id, saved_text FROM user_data")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all user data: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        self.conn.close()


# Global database manager instance
db_manager = DatabaseManager()
