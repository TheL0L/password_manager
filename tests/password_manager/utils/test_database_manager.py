import pytest
import sqlite3
from password_manager.utils.database_manager import DatabaseManager
import os

# Define a fixture for an in-memory database manager
@pytest.fixture
def db_manager():
    """
    Provides a DatabaseManager instance connected to an in-memory SQLite database
    for testing purposes. Ensures a clean slate for each test.
    """
    # Use ':memory:' for an in-memory database, which is perfect for testing
    manager = DatabaseManager(db_file=':memory:')
    yield manager
    manager.close()

class TestDatabaseManager:
    """
    Test suite for the DatabaseManager class.
    """

    def test_connection_and_table_creation(self, db_manager):
        """
        Test that the database connects and tables are created successfully.
        """
        # The db_manager fixture already connects and creates tables in __init__
        # We just need to verify that the tables exist.
        cursor = db_manager.conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        assert cursor.fetchone() is not None, "Users table should exist"

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entries';")
        assert cursor.fetchone() is not None, "Entries table should exist"

    def test_add_user_success(self, db_manager):
        """
        Test successful addition of a new user.
        """
        username = "testuser"
        salt = os.urandom(16)
        key_hash = os.urandom(32)

        user_id = db_manager.add_user(username, salt, key_hash)
        assert user_id is not None
        assert isinstance(user_id, int)
        assert user_id > 0

        # Verify the user exists in the database
        user_data = db_manager.get_user_by_username(username)
        assert user_data is not None
        assert user_data[0] == user_id
        assert user_data[1] == username
        assert user_data[2] == salt
        assert user_data[3] == key_hash

    def test_add_user_duplicate_username(self, db_manager):
        """
        Test that adding a user with an existing username returns None.
        """
        username = "duplicateuser"
        salt = os.urandom(16)
        key_hash = os.urandom(32)

        db_manager.add_user(username, salt, key_hash) # First add
        duplicate_user_id = db_manager.add_user(username, salt, key_hash) # Second add

        assert duplicate_user_id is None # Should return None for duplicate

    def test_get_user_by_username_found(self, db_manager):
        """
        Test retrieving an existing user by username.
        """
        username = "findme"
        salt = os.urandom(16)
        key_hash = os.urandom(32)
        expected_id = db_manager.add_user(username, salt, key_hash)

        user_data = db_manager.get_user_by_username(username)
        assert user_data is not None
        assert user_data[0] == expected_id
        assert user_data[1] == username
        assert user_data[2] == salt
        assert user_data[3] == key_hash

    def test_get_user_by_username_not_found(self, db_manager):
        """
        Test retrieving a non-existent user by username returns None.
        """
        user_data = db_manager.get_user_by_username("nonexistent")
        assert user_data is None

    def test_update_user_master_key_details_success(self, db_manager):
        """
        Test successful update of user master key details.
        """
        username = "updateuser"
        old_salt = os.urandom(16)
        old_hash = os.urandom(32)
        user_id = db_manager.add_user(username, old_salt, old_hash)

        new_salt = os.urandom(16)
        new_hash = os.urandom(32)

        updated = db_manager.update_user_master_key_details(user_id, new_salt, new_hash)
        assert updated is True

        # Verify updated details
        user_data = db_manager.get_user_by_username(username)
        assert user_data[2] == new_salt
        assert user_data[3] == new_hash

    def test_update_user_master_key_details_non_existent_user(self, db_manager):
        """
        Test updating master key details for a non-existent user returns False.
        """
        new_salt = os.urandom(16)
        new_hash = os.urandom(32)
        updated = db_manager.update_user_master_key_details(999, new_salt, new_hash) # Non-existent ID
        assert updated is False

    def test_add_entry_success(self, db_manager):
        """
        Test successful addition of a new entry for a user.
        """
        user_id = db_manager.add_user("entryuser", os.urandom(16), os.urandom(32))
        entry_name = "Website Login"
        encrypted_data = b"encrypted_login_data"

        entry_id = db_manager.add_entry(user_id, entry_name, encrypted_data)
        assert entry_id is not None
        assert isinstance(entry_id, int)
        assert entry_id > 0

        # Verify the entry exists
        entries = db_manager.get_entries_by_user_id(user_id)
        assert len(entries) == 1
        assert entries[0][0] == entry_id
        assert entries[0][1] == user_id
        assert entries[0][2] == entry_name
        assert entries[0][3] == encrypted_data

    def test_get_entries_by_user_id(self, db_manager):
        """
        Test retrieving all entries for a specific user.
        """
        user1_id = db_manager.add_user("user1", os.urandom(16), os.urandom(32))
        user2_id = db_manager.add_user("user2", os.urandom(16), os.urandom(32))

        db_manager.add_entry(user1_id, "Entry A", b"data_a")
        db_manager.add_entry(user1_id, "Entry B", b"data_b")
        db_manager.add_entry(user2_id, "Entry C", b"data_c")

        user1_entries = db_manager.get_entries_by_user_id(user1_id)
        user2_entries = db_manager.get_entries_by_user_id(user2_id)
        non_existent_entries = db_manager.get_entries_by_user_id(999)

        assert len(user1_entries) == 2
        assert len(user2_entries) == 1
        assert len(non_existent_entries) == 0

        # Check content of user1_entries
        assert any(e[2] == "Entry A" for e in user1_entries)
        assert any(e[2] == "Entry B" for e in user1_entries)

    def test_get_entry_by_id_found(self, db_manager):
        """
        Test retrieving a single entry by ID for a specific user.
        """
        user_id = db_manager.add_user("singleentryuser", os.urandom(16), os.urandom(32))
        entry_name = "Specific Entry"
        encrypted_data = b"specific_data"
        expected_entry_id = db_manager.add_entry(user_id, entry_name, encrypted_data)

        entry = db_manager.get_entry_by_id(expected_entry_id, user_id)
        assert entry is not None
        assert entry[0] == expected_entry_id
        assert entry[1] == user_id
        assert entry[2] == entry_name
        assert entry[3] == encrypted_data

    def test_get_entry_by_id_not_found(self, db_manager):
        """
        Test retrieving a non-existent entry by ID returns None.
        """
        user_id = db_manager.add_user("anotheruser", os.urandom(16), os.urandom(32))
        entry = db_manager.get_entry_by_id(999, user_id) # Non-existent entry ID
        assert entry is None

    def test_get_entry_by_id_wrong_user(self, db_manager):
        """
        Test retrieving an entry with correct ID but wrong user ID returns None.
        """
        user1_id = db_manager.add_user("user_a", os.urandom(16), os.urandom(32))
        user2_id = db_manager.add_user("user_b", os.urandom(16), os.urandom(32))
        entry_id = db_manager.add_entry(user1_id, "User A's Entry", b"user_a_data")

        entry = db_manager.get_entry_by_id(entry_id, user2_id) # Try to get user1's entry with user2's ID
        assert entry is None

    def test_update_entry_success(self, db_manager):
        """
        Test successful update of an existing entry.
        """
        user_id = db_manager.add_user("update_test_user", os.urandom(16), os.urandom(32))
        entry_id = db_manager.add_entry(user_id, "Old Name", b"old_data")

        new_name = "New Name"
        new_data = b"new_encrypted_data"
        updated = db_manager.update_entry(entry_id, user_id, new_name, new_data)
        assert updated is True

        # Verify the update
        entry = db_manager.get_entry_by_id(entry_id, user_id)
        assert entry[2] == new_name
        assert entry[3] == new_data

    def test_update_entry_non_existent(self, db_manager):
        """
        Test updating a non-existent entry returns False.
        """
        user_id = db_manager.add_user("update_fail_user", os.urandom(16), os.urandom(32))
        updated = db_manager.update_entry(999, user_id, "Fake Name", b"fake_data") # Non-existent entry ID
        assert updated is False

    def test_update_entry_wrong_user(self, db_manager):
        """
        Test updating an entry with correct ID but wrong user ID returns False.
        """
        user1_id = db_manager.add_user("update_user1", os.urandom(16), os.urandom(32))
        user2_id = db_manager.add_user("update_user2", os.urandom(16), os.urandom(32))
        entry_id = db_manager.add_entry(user1_id, "User1's Entry", b"user1_data")

        updated = db_manager.update_entry(entry_id, user2_id, "Attempted Update", b"new_data")
        assert updated is False

        # Ensure original entry is unchanged
        entry = db_manager.get_entry_by_id(entry_id, user1_id)
        assert entry[2] == "User1's Entry"
        assert entry[3] == b"user1_data"

    def test_delete_entry_success(self, db_manager):
        """
        Test successful deletion of an entry.
        """
        user_id = db_manager.add_user("delete_test_user", os.urandom(16), os.urandom(32))
        entry_id = db_manager.add_entry(user_id, "Entry to Delete", b"data_to_delete")

        deleted = db_manager.delete_entry(entry_id, user_id)
        assert deleted is True

        # Verify deletion
        entry = db_manager.get_entry_by_id(entry_id, user_id)
        assert entry is None
        entries = db_manager.get_entries_by_user_id(user_id)
        assert len(entries) == 0

    def test_delete_entry_non_existent(self, db_manager):
        """
        Test deleting a non-existent entry returns False.
        """
        user_id = db_manager.add_user("delete_fail_user", os.urandom(16), os.urandom(32))
        deleted = db_manager.delete_entry(999, user_id) # Non-existent entry ID
        assert deleted is False

    def test_delete_entry_wrong_user(self, db_manager):
        """
        Test deleting an entry with correct ID but wrong user ID returns False.
        """
        user1_id = db_manager.add_user("delete_user1", os.urandom(16), os.urandom(32))
        user2_id = db_manager.add_user("delete_user2", os.urandom(16), os.urandom(32))
        entry_id = db_manager.add_entry(user1_id, "User1's Entry", b"user1_data")

        deleted = db_manager.delete_entry(entry_id, user2_id)
        assert deleted is False

        # Ensure original entry is still present
        entry = db_manager.get_entry_by_id(entry_id, user1_id)
        assert entry is not None

    def test_close_connection(self, db_manager):
        """
        Test that the close method correctly closes the database connection.
        """
        db_manager.close()
        assert db_manager.conn is None
        assert db_manager.cursor is None
        # Attempting an operation after closing should raise an error
        with pytest.raises((sqlite3.ProgrammingError, AttributeError)):
            db_manager.add_user("closed_user", os.urandom(16), os.urandom(32))

    def test_del_closes_connection(self):
        """
        Test that the __del__ method (implicitly) closes the connection.
        This is harder to test directly due to Python's garbage collection,
        but we can simulate it.
        """
        # Create a manager, then delete its reference to trigger __del__
        manager = DatabaseManager(db_file=':memory:')
        conn_before_del = manager.conn
        del manager # This should trigger __del__

        # Try to use the connection directly (it should be closed)
        with pytest.raises((sqlite3.ProgrammingError, AttributeError)):
            conn_before_del.execute("SELECT 1;")
