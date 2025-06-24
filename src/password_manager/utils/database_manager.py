import sqlite3
from pathlib import Path
import logging

class DatabaseManager:
    """
    Manages SQLite database interactions for the password manager.
    This class handles connecting to the database, creating necessary tables,
    and performing CRUD operations for users and password entries.
    """

    def __init__(self, db_file: str = 'password_manager.db'):
        """
        Initializes the DatabaseManager.
        Args:
            db_file (str): The name of the SQLite database file.
        """
        self.db_path = Path(db_file)
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """
        Establishes a connection to the SQLite database.
        """
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logging.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def _create_tables(self):
        """
        Creates the 'users' and 'entries' tables if they do not already exist.
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    master_key_salt BLOB NOT NULL,
                    master_key_hash BLOB NOT NULL
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    entry_name TEXT NOT NULL,
                    encrypted_entry_data BLOB NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            self.conn.commit()
            logging.info("Tables checked/created successfully.")
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            raise

    def close(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logging.info(f"Database connection to {self.db_path} closed.")

    def add_user(self, username: str, master_key_salt: bytes, master_key_hash: bytes) -> int | None:
        """Adds a new user to the 'users' table."""
        try:
            self.cursor.execute(
                "INSERT INTO users (username, master_key_salt, master_key_hash) VALUES (?, ?, ?)",
                (username, master_key_salt, master_key_hash)
            )
            self.conn.commit()
            logging.info(f"User '{username}' added successfully with ID {self.cursor.lastrowid}.")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            logging.warning(f"Attempt to add existing user '{username}'.")
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding user '{username}': {e}")
            return None

    def get_user_by_username(self, username: str) -> tuple | None:
        """Retrieves user information by username."""
        try:
            self.cursor.execute("SELECT id, username, master_key_salt, master_key_hash FROM users WHERE username = ?", (username,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user '{username}': {e}")
            return None

    def update_user_master_key_details(self, user_id: int, new_salt: bytes, new_hash: bytes) -> bool:
        """Updates the master key details for a given user."""
        try:
            self.cursor.execute(
                "UPDATE users SET master_key_salt = ?, master_key_hash = ? WHERE id = ?",
                (new_salt, new_hash, user_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logging.info(f"Master key details updated for user ID: {user_id}.")
                return True
            else:
                logging.warning(f"Attempted to update master key for non-existent user ID: {user_id}.")
                return False
        except sqlite3.Error as e:
            logging.error(f"Error updating user master key details for user ID {user_id}: {e}")
            return False

    def add_entry(self, user_id: int, entry_name: str, encrypted_entry_data: bytes) -> int | None:
        """Adds a new encrypted password entry for a specific user."""
        try:
            self.cursor.execute(
                "INSERT INTO entries (user_id, entry_name, encrypted_entry_data) VALUES (?, ?, ?)",
                (user_id, entry_name, encrypted_entry_data)
            )
            self.conn.commit()
            logging.info(f"Entry '{entry_name}' added for user ID {user_id}.")
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Error adding entry for user ID {user_id}: {e}")
            return None

    def get_entries_by_user_id(self, user_id: int) -> list[tuple]:
        """Retrieves all encrypted password entries for a given user."""
        try:
            self.cursor.execute("SELECT id, user_id, entry_name, encrypted_entry_data FROM entries WHERE user_id = ?", (user_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving entries for user ID {user_id}: {e}")
            return []

    def get_entry_by_id(self, entry_id: int, user_id: int) -> tuple | None:
        """Retrieves a single encrypted password entry by its ID, scoped to a user."""
        try:
            self.cursor.execute("SELECT id, user_id, entry_name, encrypted_entry_data FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving entry by ID {entry_id} for user ID {user_id}: {e}")
            return None

    def update_entry(self, entry_id: int, user_id: int, new_entry_name: str, new_encrypted_data: bytes) -> bool:
        """Updates an existing encrypted password entry."""
        try:
            self.cursor.execute(
                "UPDATE entries SET entry_name = ?, encrypted_entry_data = ? WHERE id = ? AND user_id = ?",
                (new_entry_name, new_encrypted_data, entry_id, user_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logging.info(f"Entry ID {entry_id} updated successfully for user ID {user_id}.")
                return True
            else:
                logging.warning(f"Attempted to update non-existent or unauthorized entry ID {entry_id}.")
                return False
        except sqlite3.Error as e:
            logging.error(f"Error updating entry ID {entry_id}: {e}")
            return False

    def delete_entry(self, entry_id: int, user_id: int) -> bool:
        """Deletes a password entry from the 'entries' table."""
        try:
            self.cursor.execute("DELETE FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                logging.info(f"Entry ID {entry_id} deleted successfully for user ID {user_id}.")
                return True
            else:
                logging.warning(f"Attempted to delete non-existent or unauthorized entry ID {entry_id}.")
                return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting entry ID {entry_id}: {e}")
            return False
            
    def __del__(self):
        """
        Ensures the database connection is closed when the object is destroyed.
        """
        self.close()
