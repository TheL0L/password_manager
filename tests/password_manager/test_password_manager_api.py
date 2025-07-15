import pytest
import json
from pytest_mock import mocker
from password_manager.password_manager_api import PasswordManagerAPI

# Fixture to provide a mocked PasswordManagerAPI instance for each test
@pytest.fixture
def api_instance(mocker): # Accept the mocker fixture
    """
    Provides a PasswordManagerAPI instance with mocked dependencies using pytest-mock.
    """
    # Patch the classes where they are imported within the password_manager_api module.
    # This ensures that when PasswordManagerAPI uses these, it uses the mocks.
    MockDBManager = mocker.patch('password_manager.password_manager_api.DatabaseManager')
    MockEncryptionHandler = mocker.patch('password_manager.password_manager_api.EncryptionHandler')
    # IMPORTANT: Patch VerificationUtils where it's imported in password_manager_api.py
    MockVerificationUtils = mocker.patch('password_manager.password_manager_api.VerificationUtils')
    MockPasswordGenerator = mocker.patch('password_manager.password_manager_api.PasswordGenerator')

    # Create an instance of the API. It will now use the patched (mocked) classes.
    api = PasswordManagerAPI(db_file=':memory:')

    # Assign the return_value of the class mocks to the API instance's attributes
    # This is correct because MockDBManager and MockEncryptionHandler are mocks of classes,
    # and their instances (what PasswordManagerAPI's __init__ creates) are accessed via .return_value.
    # For static methods like VerificationUtils and PasswordGenerator, the mock class itself is used.
    api.db_manager = MockDBManager.return_value
    api.encryption_handler = MockEncryptionHandler.return_value
    api.verification_utils = MockVerificationUtils
    api.password_generator = MockPasswordGenerator

    yield api


class TestUserManagement:
    """
    Test suite for user registration, login, logout, and status checks in PasswordManagerAPI.
    """

    def test_register_user_success(self, api_instance):
        """
        Test successful user registration.
        """
        # Set return values directly on the mocked static methods
        api_instance.verification_utils.is_valid_username.return_value = (True, "")
        api_instance.db_manager.get_user_by_username.return_value = None # User does not exist
        api_instance.encryption_handler.generate_salt.return_value = b"test_salt"
        api_instance.encryption_handler.derive_key.return_value = b"derived_key_hash"
        api_instance.db_manager.add_user.return_value = 1 # User ID

        success, message = api_instance.register_user("newuser", "MasterPass123!")

        assert success is True
        assert message != "" # Check that a message is returned
        api_instance.verification_utils.is_valid_username.assert_called_once_with("newuser")
        api_instance.db_manager.get_user_by_username.assert_called_once_with("newuser")
        api_instance.encryption_handler.generate_salt.assert_called_once()
        api_instance.encryption_handler.derive_key.assert_called_once_with("MasterPass123!", b"test_salt")
        api_instance.db_manager.add_user.assert_called_once_with("newuser", b"test_salt", b"derived_key_hash")

    def test_register_user_invalid_username(self, api_instance):
        """
        Test user registration with an invalid username.
        """
        api_instance.verification_utils.is_valid_username.return_value = (False, "Invalid username format")

        success, message = api_instance.register_user("bad user", "MasterPass123!")

        assert success is False
        assert "Invalid" in message # Check for generic invalid message
        api_instance.verification_utils.is_valid_username.assert_called_once_with("bad user")
        # These should not be called if validation fails early
        api_instance.db_manager.get_user_by_username.assert_not_called()
        api_instance.encryption_handler.generate_salt.assert_not_called()

    def test_register_user_username_exists(self, api_instance):
        """
        Test user registration when the username already exists.
        """
        api_instance.verification_utils.is_valid_username.return_value = (True, "")
        api_instance.db_manager.get_user_by_username.return_value = (1, "existinguser", b"salt", b"hash")

        success, message = api_instance.register_user("existinguser", "MasterPass123!")

        assert success is False
        assert message != "" # Check that a message is returned for existing user
        api_instance.db_manager.get_user_by_username.assert_called_once_with("existinguser")
        api_instance.encryption_handler.generate_salt.assert_not_called()

    def test_register_user_db_add_failure(self, api_instance):
        """
        Test user registration when adding to the database fails.
        """
        api_instance.verification_utils.is_valid_username.return_value = (True, "")
        api_instance.db_manager.get_user_by_username.return_value = None
        api_instance.encryption_handler.generate_salt.return_value = b"test_salt"
        api_instance.encryption_handler.derive_key.return_value = b"derived_key_hash"
        api_instance.db_manager.add_user.return_value = None # Simulate DB failure

        success, message = api_instance.register_user("dbfailuser", "MasterPass123!")

        assert success is False
        assert "Failed" in message # Check for generic failed message
        api_instance.db_manager.add_user.assert_called_once()

    def test_login_user_success(self, api_instance):
        """
        Test successful user login.
        """
        username = "testuser"
        master_password = "MasterPass123!"
        stored_salt = b"stored_salt"
        # Directly set the return value for encryption_handler.derive_key
        # as it's a static method on the mocked class.
        api_instance.encryption_handler.derive_key.return_value = b"derived_key_hash"

        api_instance.db_manager.get_user_by_username.return_value = (1, username, stored_salt, b"derived_key_hash")

        success, message = api_instance.login_user(username, master_password)

        assert success is True
        assert message != "" # Check that a message is returned
        assert api_instance.current_user_id == 1
        assert api_instance.current_username == username
        assert api_instance.current_master_key == b"derived_key_hash"
        api_instance.db_manager.get_user_by_username.assert_called_once_with(username)
        api_instance.encryption_handler.derive_key.assert_called_once_with(master_password, stored_salt)

    def test_login_user_invalid_username(self, api_instance):
        """
        Test user login with a non-existent username.
        """
        api_instance.db_manager.get_user_by_username.return_value = None

        success, message = api_instance.login_user("nonexistent", "password")

        assert success is False
        assert "Invalid" in message # Check for generic invalid message
        assert api_instance.current_user_id is None
        api_instance.db_manager.get_user_by_username.assert_called_once_with("nonexistent")
        api_instance.encryption_handler.derive_key.assert_not_called()

    def test_login_user_incorrect_password(self, api_instance):
        """
        Test user login with an incorrect master password.
        """
        username = "testuser"
        wrong_password = "WrongPass!"
        stored_salt = b"stored_salt"
        correct_derived_key = b"correct_derived_key"
        wrong_derived_key_attempt = b"wrong_derived_key" # Simulate a different key

        api_instance.db_manager.get_user_by_username.return_value = (1, username, stored_salt, correct_derived_key)
        # Mock derive_key to return the wrong key for the wrong password attempt
        api_instance.encryption_handler.derive_key.return_value = wrong_derived_key_attempt

        success, message = api_instance.login_user(username, wrong_password)

        assert success is False
        assert "Invalid" in message # Check for generic invalid message
        assert api_instance.current_user_id is None
        api_instance.encryption_handler.derive_key.assert_called_once_with(wrong_password, stored_salt)

    def test_logout_user(self, api_instance):
        """
        Test user logout functionality.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"some_key"
        api_instance.current_username = "logged_in_user"

        success, message = api_instance.logout_user()

        assert success is True
        assert message != "" # Check that a message is returned
        assert api_instance.current_user_id is None
        assert api_instance.current_master_key is None
        assert api_instance.current_username is None

    def test_is_logged_in(self, api_instance):
        """
        Test is_logged_in method.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"some_key"
        assert api_instance.is_logged_in() is True

        api_instance.current_user_id = None
        assert api_instance.is_logged_in() is False

        api_instance.current_user_id = 1
        api_instance.current_master_key = None
        assert api_instance.is_logged_in() is False


class TestEntryManagement:
    """
    Test suite for adding, viewing, editing, and removing password entries in PasswordManagerAPI.
    """

    @pytest.mark.parametrize("valid_name, valid_address, valid_username, valid_password, valid_notes, expected_success", [
        (True, True, True, True, True, True),  # All valid
        (False, True, True, True, True, False), # Invalid name
        (True, False, True, True, True, False), # Invalid address
        (True, True, False, True, True, False), # Invalid username field
        (True, True, True, False, True, False), # Invalid password field
        (True, True, True, True, False, False), # Invalid notes
    ])
    def test_add_entry_validation(self, api_instance, valid_name, valid_address, valid_username, valid_password, valid_notes, expected_success):
        """
        Test add_entry with various validation scenarios.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"

        # Set return values for all validation static methods
        api_instance.verification_utils.is_valid_entry_name.return_value = (valid_name, "Invalid name" if not valid_name else "")
        api_instance.verification_utils.is_valid_address.return_value = (valid_address, "Invalid address" if not valid_address else "")
        api_instance.verification_utils.is_valid_entry_username_field.return_value = (valid_username, "Invalid entry username" if not valid_username else "")
        api_instance.verification_utils.is_valid_entry_password_field.return_value = (valid_password, "Invalid entry password" if not valid_password else "")
        api_instance.verification_utils.is_valid_entry_notes.return_value = (valid_notes, "Invalid notes" if not valid_notes else "")

        success, message = api_instance.add_entry("Test Name", "test.com", "testuser", "pass", "notes")

        assert success is expected_success
        if not expected_success:
            assert "Invalid" in message # Check for any validation error message
        else:
            api_instance.encryption_handler.encrypt_data.assert_called_once()
            api_instance.db_manager.add_entry.assert_called_once()

    def test_add_entry_not_logged_in(self, api_instance):
        """
        Test add_entry when no user is logged in.
        """
        api_instance.current_user_id = None # Ensure not logged in
        success, message = api_instance.add_entry("Name", "Addr", "User", "Pass", "Notes")
        assert success is False
        assert message != "" # Check that a message is returned
        api_instance.encryption_handler.encrypt_data.assert_not_called()
        api_instance.db_manager.add_entry.assert_not_called()

    def test_add_entry_encryption_failure(self, api_instance):
        """
        Test add_entry when encryption fails.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        api_instance.verification_utils.is_valid_entry_name.return_value = (True, "")
        api_instance.verification_utils.is_valid_address.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_username_field.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_password_field.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_notes.return_value = (True, "")
        api_instance.encryption_handler.encrypt_data.side_effect = Exception("Encryption error")

        success, message = api_instance.add_entry("Test Name", "test.com", "testuser", "pass", "notes")

        assert success is False
        assert "failed" in message # Check for generic failed message
        api_instance.encryption_handler.encrypt_data.assert_called_once()
        api_instance.db_manager.add_entry.assert_not_called()

    def test_add_entry_db_failure(self, api_instance):
        """
        Test add_entry when database addition fails.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        api_instance.verification_utils.is_valid_entry_name.return_value = (True, "")
        api_instance.verification_utils.is_valid_address.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_username_field.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_password_field.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_notes.return_value = (True, "")
        api_instance.encryption_handler.encrypt_data.return_value = b"encrypted_data"
        api_instance.db_manager.add_entry.return_value = None # Simulate DB failure

        success, message = api_instance.add_entry("Test Name", "test.com", "testuser", "pass", "notes")

        assert success is False
        assert "Failed" in message # Check for generic failed message
        api_instance.db_manager.add_entry.assert_called_once()

    def test_view_entries_success(self, api_instance):
        """
        Test successful retrieval and decryption of entries.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        encrypted_data_1 = b"encrypted_data_1"
        encrypted_data_2 = b"encrypted_data_2"
        decrypted_json_1 = json.dumps({"Name": "Entry 1", "Address": "a.com", "Username": "u1", "Password": "p1", "Notes": ""})
        decrypted_json_2 = json.dumps({"Name": "Entry 2", "Address": "b.com", "Username": "u2", "Password": "p2", "Notes": ""})

        api_instance.db_manager.get_entries_by_user_id.return_value = [
            (101, 1, "Entry 1", encrypted_data_1),
            (102, 1, "Entry 2", encrypted_data_2)
        ]
        api_instance.encryption_handler.decrypt_data.side_effect = [
            decrypted_json_1,
            decrypted_json_2
        ]

        success, entries = api_instance.view_entries()

        assert success is True
        assert len(entries) == 2
        assert entries[0]['id'] == 101
        assert entries[0]['EntryName'] == "Entry 1"
        assert entries[0]['Username'] == "u1"
        assert entries[1]['id'] == 102
        assert entries[1]['EntryName'] == "Entry 2"
        assert entries[1]['Username'] == "u2"
        api_instance.db_manager.get_entries_by_user_id.assert_called_once_with(1)
        api_instance.encryption_handler.decrypt_data.assert_any_call(b"master_key", encrypted_data_1)
        api_instance.encryption_handler.decrypt_data.assert_any_call(b"master_key", encrypted_data_2)

    def test_view_entries_no_entries(self, api_instance):
        """
        Test view_entries when there are no entries for the user.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        api_instance.db_manager.get_entries_by_user_id.return_value = []

        success, entries = api_instance.view_entries()

        assert success is True
        assert entries == []
        api_instance.db_manager.get_entries_by_user_id.assert_called_once_with(1)
        api_instance.encryption_handler.decrypt_data.assert_not_called()

    def test_view_entries_not_logged_in(self, api_instance):
        """
        Test view_entries when no user is logged in.
        """
        api_instance.current_user_id = None
        success, message = api_instance.view_entries()
        assert success is False
        assert message != "" # Check that a message is returned
        api_instance.db_manager.get_entries_by_user_id.assert_not_called()

    def test_view_entries_decryption_failure_skips_entry(self, api_instance):
        """
        Test view_entries handles decryption failures gracefully by skipping the entry.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        encrypted_data_good = b"encrypted_data_good"
        encrypted_data_bad = b"encrypted_data_bad"
        decrypted_json_good = json.dumps({"Name": "Good Entry", "Address": "g.com", "Username": "gu", "Password": "gp", "Notes": ""})

        api_instance.db_manager.get_entries_by_user_id.return_value = [
            (101, 1, "Good Entry", encrypted_data_good),
            (102, 1, "Bad Entry", encrypted_data_bad) # This one will fail decryption
        ]
        api_instance.encryption_handler.decrypt_data.side_effect = [
            decrypted_json_good,
            None # Simulate decryption failure
        ]

        success, entries = api_instance.view_entries()

        assert success is True
        assert len(entries) == 1 # Only the good entry should be returned
        assert entries[0]['id'] == 101
        assert entries[0]['EntryName'] == "Good Entry"
        assert api_instance.encryption_handler.decrypt_data.call_count == 2 # Both attempts should be made

    def test_get_entry_by_id_success(self, api_instance):
        """
        Test successful retrieval and decryption of a single entry by ID.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        entry_id = 101
        encrypted_data = b"encrypted_single_data"
        decrypted_json = json.dumps({"Name": "Single Entry", "Address": "s.com", "Username": "su", "Password": "sp", "Notes": ""})

        api_instance.db_manager.get_entry_by_id.return_value = (entry_id, 1, "Single Entry", encrypted_data)
        api_instance.encryption_handler.decrypt_data.return_value = decrypted_json

        success, entry = api_instance.get_entry_by_id(entry_id)

        assert success is True
        assert entry['id'] == entry_id
        assert entry['EntryName'] == "Single Entry"
        assert entry['Username'] == "su"
        api_instance.db_manager.get_entry_by_id.assert_called_once_with(entry_id, 1)
        api_instance.encryption_handler.decrypt_data.assert_called_once_with(b"master_key", encrypted_data)

    def test_get_entry_by_id_not_logged_in(self, api_instance):
        """
        Test get_entry_by_id when no user is logged in.
        """
        api_instance.current_user_id = None
        success, message = api_instance.get_entry_by_id(1)
        assert success is False
        assert message != "" # Check that a message is returned
        api_instance.db_manager.get_entry_by_id.assert_not_called()

    def test_get_entry_by_id_not_found(self, api_instance):
        """
        Test get_entry_by_id when the entry is not found.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        api_instance.db_manager.get_entry_by_id.return_value = None

        success, message = api_instance.get_entry_by_id(999)

        assert success is False
        assert message != "" # Check that a message is returned
        api_instance.db_manager.get_entry_by_id.assert_called_once_with(999, 1)
        api_instance.encryption_handler.decrypt_data.assert_not_called()

    def test_get_entry_by_id_decryption_failure(self, api_instance):
        """
        Test get_entry_by_id when decryption fails.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        entry_id = 101
        encrypted_data = b"corrupt_encrypted_data"

        api_instance.db_manager.get_entry_by_id.return_value = (entry_id, 1, "Corrupt Entry", encrypted_data)
        api_instance.encryption_handler.decrypt_data.return_value = None # Simulate decryption failure

        success, message = api_instance.get_entry_by_id(entry_id)

        assert success is False
        assert "Failed" in message # Check for generic failed message
        api_instance.encryption_handler.decrypt_data.assert_called_once_with(b"master_key", encrypted_data)

    @pytest.mark.parametrize("valid_name, valid_address, valid_username, valid_password, valid_notes, expected_success", [
        (True, True, True, True, True, True),  # All valid
        (False, True, True, True, True, False), # Invalid name
    ])
    def test_edit_entry_validation(self, api_instance, valid_name, valid_address, valid_username, valid_password, valid_notes, expected_success):
        """
        Test edit_entry with various validation scenarios.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        api_instance.db_manager.update_entry.return_value = True # Assume DB update would succeed if reached

        api_instance.verification_utils.is_valid_entry_name.return_value = (valid_name, "Invalid name" if not valid_name else "")
        api_instance.verification_utils.is_valid_address.return_value = (valid_address, "Invalid address" if not valid_address else "")
        api_instance.verification_utils.is_valid_entry_username_field.return_value = (valid_username, "Invalid entry username" if not valid_username else "")
        api_instance.verification_utils.is_valid_entry_password_field.return_value = (valid_password, "Invalid entry password" if not valid_password else "")
        api_instance.verification_utils.is_valid_entry_notes.return_value = (valid_notes, "Invalid notes" if not valid_notes else "")

        success, message = api_instance.edit_entry(101, "New Name", "new.com", "newuser", "newpass", "newnotes")

        assert success is expected_success
        if not expected_success:
            assert "Invalid" in message
        else:
            api_instance.encryption_handler.encrypt_data.assert_called_once()
            api_instance.db_manager.update_entry.assert_called_once()

    def test_edit_entry_not_logged_in(self, api_instance):
        """
        Test edit_entry when no user is logged in.
        """
        api_instance.current_user_id = None
        success, message = api_instance.edit_entry(1, "N", "A", "U", "P", "N")
        assert success is False
        assert message != "" # Check that a message is returned
        api_instance.encryption_handler.encrypt_data.assert_not_called()
        api_instance.db_manager.update_entry.assert_not_called()

    def test_edit_entry_encryption_failure(self, api_instance):
        """
        Test edit_entry when encryption fails during update.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        api_instance.verification_utils.is_valid_entry_name.return_value = (True, "")
        api_instance.verification_utils.is_valid_address.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_username_field.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_password_field.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_notes.return_value = (True, "")
        api_instance.encryption_handler.encrypt_data.side_effect = Exception("Encryption error")

        success, message = api_instance.edit_entry(101, "New Name", "new.com", "newuser", "newpass", "newnotes")

        assert success is False
        assert "failed" in message # Check for generic failed message
        api_instance.encryption_handler.encrypt_data.assert_called_once()
        api_instance.db_manager.update_entry.assert_not_called()

    def test_edit_entry_db_update_failure(self, api_instance):
        """
        Test edit_entry when database update fails.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"master_key"
        api_instance.verification_utils.is_valid_entry_name.return_value = (True, "")
        api_instance.verification_utils.is_valid_address.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_username_field.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_password_field.return_value = (True, "")
        api_instance.verification_utils.is_valid_entry_notes.return_value = (True, "")
        api_instance.encryption_handler.encrypt_data.return_value = b"new_encrypted_data"
        api_instance.db_manager.update_entry.return_value = False # Simulate DB update failure

        success, message = api_instance.edit_entry(101, "New Name", "new.com", "newuser", "newpass", "newnotes")

        assert success is False
        assert "Failed" in message # Check for generic failed message
        api_instance.db_manager.update_entry.assert_called_once()

    def test_remove_entry_success(self, api_instance):
        """
        Test successful removal of an entry.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"some_master_key"
        api_instance.db_manager.delete_entry.return_value = True

        success, message = api_instance.remove_entry(101)

        assert success is True
        assert message != "" # Check that a message is returned
        api_instance.db_manager.delete_entry.assert_called_once_with(101, 1)

    def test_remove_entry_not_logged_in(self, api_instance):
        """
        Test remove_entry when no user is logged in.
        """
        api_instance.current_user_id = None
        success, message = api_instance.remove_entry(1)
        assert success is False
        assert message != "" # Check that a message is returned
        api_instance.db_manager.delete_entry.assert_not_called()

    def test_remove_entry_db_failure(self, api_instance):
        """
        Test remove_entry when database deletion fails.
        """
        api_instance.current_user_id = 1
        api_instance.current_master_key = b"some_master_key"
        api_instance.db_manager.delete_entry.return_value = False

        success, message = api_instance.remove_entry(101)

        assert success is False
        assert "Failed" in message # Check for generic failed message
        api_instance.db_manager.delete_entry.assert_called_once_with(101, 1)


class TestMasterPasswordChange:
    """
    Test suite for changing the master password in PasswordManagerAPI.
    """

    def test_change_master_password_success(self, api_instance):
        """
        Test successful master password change with re-encryption of entries.
        """
        username = "testuser"
        old_password = "OldPass123!"
        new_password = "NewPass123!"
        user_id = 1
        old_salt = b"old_salt"
        old_derived_key = b"old_derived_key" # Use simple bytes for mock return
        new_salt = b"new_salt"
        new_derived_key = b"new_derived_key" # Use simple bytes for mock return

        api_instance.current_user_id = user_id
        api_instance.current_master_key = old_derived_key
        api_instance.current_username = username

        # Mock _load_user_data via db_manager.get_user_by_username
        api_instance.db_manager.get_user_by_username.return_value = (user_id, username, old_salt, old_derived_key)
        
        # Mock derive_key for old password verification and new key derivation
        # Use side_effect to return different values for sequential calls
        api_instance.encryption_handler.derive_key.side_effect = [
            old_derived_key, # First call: for verifying old password
            new_derived_key  # Second call: for deriving new key
        ]
        api_instance.encryption_handler.generate_salt.return_value = new_salt # For new salt

        # Mock view_entries to return some entries
        entry_json_1 = json.dumps({"Name": "Entry 1", "Address": "a.com", "Username": "u1", "Password": "p1", "Notes": ""})
        entry_json_2 = json.dumps({"Name": "Entry 2", "Address": "b.com", "Username": "u2", "Password": "p2", "Notes": ""})
        api_instance.db_manager.get_entries_by_user_id.return_value = [
            (201, user_id, "Entry 1", b"old_encrypted_data_1"),
            (202, user_id, "Entry 2", b"old_encrypted_data_2")
        ]
        api_instance.encryption_handler.decrypt_data.side_effect = [
            entry_json_1,
            entry_json_2
        ]
        api_instance.encryption_handler.encrypt_data.side_effect = [
            b"new_encrypted_data_1",
            b"new_encrypted_data_2"
        ]
        api_instance.db_manager.update_entry.return_value = True # Assume updates succeed
        api_instance.db_manager.update_user_master_key_details.return_value = True

        success, message = api_instance.change_master_password(old_password, new_password)

        assert success is True
        assert message != "" # Check that a message is returned
        assert api_instance.current_master_key == new_derived_key
        api_instance.db_manager.get_user_by_username.assert_called_once_with(username)
        assert api_instance.encryption_handler.derive_key.call_count == 2
        api_instance.encryption_handler.generate_salt.assert_called_once()
        api_instance.db_manager.get_entries_by_user_id.assert_called_once_with(user_id)
        assert api_instance.encryption_handler.decrypt_data.call_count == 2
        assert api_instance.encryption_handler.encrypt_data.call_count == 2
        assert api_instance.db_manager.update_entry.call_count == 2
        api_instance.db_manager.update_user_master_key_details.assert_called_once_with(user_id, new_salt, new_derived_key)

    def test_change_master_password_not_logged_in(self, api_instance):
        """
        Test change_master_password when no user is logged in.
        """
        api_instance.current_user_id = None
        success, message = api_instance.change_master_password("old", "new")
        assert success is False
        assert message != "" # Check that a message is returned
        api_instance.db_manager.get_user_by_username.assert_not_called()

    def test_change_master_password_incorrect_old_password(self, api_instance):
        """
        Test change_master_password with an incorrect old master password.
        """
        username = "testuser"
        old_password = "OldPass123!"
        wrong_old_password = "WrongOldPass!"
        new_password = "NewPass123!"
        user_id = 1
        stored_salt = b"stored_salt"
        correct_derived_key = b"correct_derived_key"
        wrong_derived_key_attempt = b"wrong_derived_key_attempt"

        api_instance.current_user_id = user_id
        api_instance.current_master_key = correct_derived_key # Assume logged in with correct key
        api_instance.current_username = username

        api_instance.db_manager.get_user_by_username.return_value = (user_id, username, stored_salt, correct_derived_key)
        # Mock derive_key to return the wrong key for the wrong password attempt
        api_instance.encryption_handler.derive_key.return_value = wrong_derived_key_attempt

        success, message = api_instance.change_master_password(wrong_old_password, new_password)

        assert success is False
        assert "Incorrect" in message # Check for generic incorrect message
        api_instance.encryption_handler.derive_key.assert_called_once_with(wrong_old_password, stored_salt)
        api_instance.db_manager.update_user_master_key_details.assert_not_called()
        api_instance.db_manager.get_entries_by_user_id.assert_not_called()


    def test_change_master_password_same_as_old(self, api_instance):
        """
        Test change_master_password when new password is the same as the old one.
        """
        username = "testuser"
        old_password = "SamePass123!"
        new_password = "SamePass123!" # Same password
        user_id = 1
        stored_salt = b"stored_salt"
        derived_key = b"derived_key"

        api_instance.current_user_id = user_id
        api_instance.current_master_key = derived_key
        api_instance.current_username = username

        api_instance.db_manager.get_user_by_username.return_value = (user_id, username, stored_salt, derived_key)
        api_instance.encryption_handler.derive_key.return_value = derived_key # For verification

        success, message = api_instance.change_master_password(old_password, new_password)

        assert success is False
        assert "cannot be the same" in message # Specific validation message
        api_instance.db_manager.update_user_master_key_details.assert_not_called()
        api_instance.db_manager.get_entries_by_user_id.assert_not_called()

    def test_change_master_password_reencryption_failure(self, api_instance):
        """
        Test change_master_password when re-encryption of an entry fails.
        """
        username = "testuser"
        old_password = "OldPass123!"
        new_password = "NewPass123!"
        user_id = 1
        old_salt = b"old_salt"
        old_derived_key = b"old_derived_key"
        new_salt = b"new_salt"
        new_derived_key = b"new_derived_key"

        api_instance.current_user_id = user_id
        api_instance.current_master_key = old_derived_key
        api_instance.current_username = username

        api_instance.db_manager.get_user_by_username.return_value = (user_id, username, old_salt, old_derived_key)
        api_instance.encryption_handler.derive_key.side_effect = [
            old_derived_key, # For verifying old password
            new_derived_key  # For deriving new key
        ]
        api_instance.encryption_handler.generate_salt.return_value = new_salt

        # Mock view_entries to return some entries, one of which will cause re-encryption to fail
        entry_json_1 = json.dumps({"Name": "Entry 1", "Address": "a.com", "Username": "u1", "Password": "p1", "Notes": ""})
        entry_json_2 = json.dumps({"Name": "Entry 2", "Address": "b.com", "Username": "u2", "Password": "p2", "Notes": ""})
        api_instance.db_manager.get_entries_by_user_id.return_value = [
            (201, user_id, "Entry 1", b"old_encrypted_data_1"),
            (202, user_id, "Entry 2", b"old_encrypted_data_2")
        ]
        api_instance.encryption_handler.decrypt_data.side_effect = [
            entry_json_1,
            entry_json_2
        ]
        # Simulate encryption failure for the second entry
        api_instance.encryption_handler.encrypt_data.side_effect = [
            b"new_encrypted_data_1",
            Exception("Re-encryption failed for this entry")
        ]

        success, message = api_instance.change_master_password(old_password, new_password)

        assert success is False
        assert "Error re-encrypting" in message # Check for generic re-encryption error
        # Check that master key details were NOT updated in DB
        api_instance.db_manager.update_user_master_key_details.assert_not_called()
        # In this API, current_master_key is only updated if db.update_user_master_key_details succeeds
        assert api_instance.current_master_key == old_derived_key


class TestPasswordGeneration:
    """
    Test suite for random password generation in PasswordManagerAPI.
    """

    @pytest.mark.parametrize("length, uc, lc, dig, sp, expected_success, expected_message_part", [
        (10, True, True, True, True, True, ""),
        (0, True, True, True, True, False, "Password length must be a positive integer."),
        (5, False, False, False, False, False, "At least one character set must be selected."),
        (10, True, False, False, False, True, ""), # Only uppercase
    ])
    def test_generate_random_password(self, api_instance, length, uc, lc, dig, sp, expected_success, expected_message_part):
        """
        Test random password generation with various parameters and failure cases.
        """
        if expected_success:
            api_instance.password_generator.generate_password.return_value = "GeneratedPassword"
        else:
            api_instance.password_generator.generate_password.return_value = None # Not called or returns None

        success, result = api_instance.generate_random_password(length, uc, lc, dig, sp)

        assert success is expected_success
        if expected_success:
            assert result == "GeneratedPassword"
            api_instance.password_generator.generate_password.assert_called_once_with(length, uc, lc, dig, sp)
        else:
            assert expected_message_part in result
            # Only assert not called if the validation prevents the call
            if "length" in expected_message_part or "character set" in expected_message_part:
                api_instance.password_generator.generate_password.assert_not_called()
            else:
                # If it's a different failure path where generate_password might still be called
                # but returns None, then assert it was called.
                api_instance.password_generator.generate_password.assert_called_once_with(length, uc, lc, dig, sp)

