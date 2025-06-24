import json
import logging
from typing import Optional, List, Dict, Tuple

from password_manager.utils.database_manager import DatabaseManager
from password_manager.utils.encryption_handler import EncryptionHandler
from password_manager.utils.verification_utils import VerificationUtils
from password_manager.utils.password_generator import PasswordGenerator

class PasswordManagerAPI:
    """
    Provides the API for the password manager application.
    This layer orchestrates interactions between the UI (or console) and the
    utility modules (database, encryption, password generation).
    """

    def __init__(self, db_file: str = 'password_manager.db'):
        """
        Initializes the PasswordManagerAPI.
        Args:
            db_file (str): The name of the SQLite database file.
        """
        self.db_manager = DatabaseManager(db_file)
        self.encryption_handler = EncryptionHandler()
        self.current_user_id: Optional[int] = None
        self.current_master_key: Optional[bytes] = None
        self.current_username: Optional[str] = None

    def __del__(self):
        """
        Ensures the database connection is closed when the API object is destroyed.
        """
        self.db_manager.close()

    def _load_user_data(self, username: str) -> Optional[Tuple[int, bytes, bytes]]:
        """Loads user data from the database."""
        user_data = self.db_manager.get_user_by_username(username)
        if user_data:
            user_id, _, master_key_salt, master_key_hash = user_data
            return user_id, master_key_salt, master_key_hash
        return None

    def register_user(self, username: str, master_password: str) -> Tuple[bool, str]:
        """Registers a new local user."""
        valid_username, msg = VerificationUtils.is_valid_username(username)
        if not valid_username:
            return False, msg

        if self.db_manager.get_user_by_username(username):
            return False, f"Username '{username}' already exists."

        salt = self.encryption_handler.generate_salt()
        derived_key = self.encryption_handler.derive_key(master_password, salt)

        user_id = self.db_manager.add_user(username, salt, derived_key)
        if user_id:
            return True, f"User '{username}' registered successfully."
        else:
            return False, "Failed to register user due to a database error."

    def login_user(self, username: str, master_password: str) -> Tuple[bool, str]:
        """Logs in a registered local user."""
        user_data = self._load_user_data(username)
        if not user_data:
            return False, "Invalid username or password."

        user_id, stored_salt, stored_derived_key = user_data
        attempted_derived_key = self.encryption_handler.derive_key(master_password, stored_salt)

        if attempted_derived_key == stored_derived_key:
            self.current_user_id = user_id
            self.current_master_key = attempted_derived_key
            self.current_username = username
            return True, f"User '{username}' logged in successfully."
        else:
            self.logout_user()
            return False, "Invalid username or password."

    def logout_user(self) -> Tuple[bool, str]:
        """Logs out the current user."""
        self.current_user_id = None
        self.current_master_key = None
        self.current_username = None
        return True, "Logged out successfully."

    def is_logged_in(self) -> bool:
        """Checks if a user is currently logged in."""
        return self.current_user_id is not None and self.current_master_key is not None

    def add_entry(self, name: str, address: str, username_entry: str, password_entry: str, notes: str) -> Tuple[bool, str]:
        """Adds a new password entry for the logged-in user."""
        if not self.is_logged_in():
            return False, "No user logged in."

        validations = [
            VerificationUtils.is_valid_entry_name(name),
            VerificationUtils.is_valid_address(address),
            VerificationUtils.is_valid_entry_username_field(username_entry),
            VerificationUtils.is_valid_entry_password_field(password_entry),
            VerificationUtils.is_valid_entry_notes(notes)
        ]
        for valid, msg in validations:
            if not valid:
                return False, msg

        entry_data = {"Name": name, "Address": address, "Username": username_entry, "Password": password_entry, "Notes": notes}
        entry_json = json.dumps(entry_data)

        try:
            encrypted_data = self.encryption_handler.encrypt_data(self.current_master_key, entry_json)
        except Exception as e:
            logging.error(f"Encryption failed for new entry: {e}")
            return False, f"Encryption failed: {e}"

        entry_id = self.db_manager.add_entry(self.current_user_id, name, encrypted_data)
        if entry_id:
            return True, f"Entry '{name}' added successfully."
        else:
            return False, "Failed to add entry due to a database error."

    def view_entries(self) -> Tuple[bool, str | List[Dict]]:
        """Retrieves and decrypts all password entries for the logged-in user."""
        if not self.is_logged_in():
            return False, "No user logged in."

        raw_entries = self.db_manager.get_entries_by_user_id(self.current_user_id)
        decrypted_entries = []
        for entry_id, user_id, entry_name, encrypted_data in raw_entries:
            try:
                decrypted_json = self.encryption_handler.decrypt_data(self.current_master_key, encrypted_data)
                if decrypted_json:
                    entry_dict = json.loads(decrypted_json)
                    entry_dict['id'] = entry_id
                    entry_dict['EntryName'] = entry_name
                    decrypted_entries.append(entry_dict)
            except (json.JSONDecodeError, Exception) as e:
                logging.warning(f"Could not parse or decrypt entry ID {entry_id}. Error: {e}")
                continue
        return True, decrypted_entries

    def get_entry_by_id(self, entry_id: int) -> Tuple[bool, str | Dict]:
        """Retrieves and decrypts a single password entry by its ID."""
        if not self.is_logged_in():
            return False, "No user logged in."

        raw_entry = self.db_manager.get_entry_by_id(entry_id, self.current_user_id)
        if not raw_entry:
            return False, f"Entry with ID {entry_id} not found."

        _, _, entry_name, encrypted_data = raw_entry
        try:
            decrypted_json = self.encryption_handler.decrypt_data(self.current_master_key, encrypted_data)
            if decrypted_json:
                entry_dict = json.loads(decrypted_json)
                entry_dict['id'] = entry_id
                entry_dict['EntryName'] = entry_name
                return True, entry_dict
            else:
                return False, "Failed to decrypt entry data. Key may be incorrect or data is corrupt."
        except (json.JSONDecodeError, Exception) as e:
            logging.error(f"Error parsing decrypted entry data for ID {entry_id}: {e}")
            return False, f"Error parsing decrypted entry data for ID {entry_id}."

    def edit_entry(self, entry_id: int, new_name: str, new_address: str, new_username_entry: str, new_password_entry: str, new_notes: str) -> Tuple[bool, str]:
        """Edits an existing password entry."""
        if not self.is_logged_in():
            return False, "No user logged in."

        validations = [
            VerificationUtils.is_valid_entry_name(new_name),
            VerificationUtils.is_valid_address(new_address),
            VerificationUtils.is_valid_entry_username_field(new_username_entry),
            VerificationUtils.is_valid_entry_password_field(new_password_entry),
            VerificationUtils.is_valid_entry_notes(new_notes)
        ]
        for valid, msg in validations:
            if not valid:
                return False, msg

        new_entry_data = {"Name": new_name, "Address": new_address, "Username": new_username_entry, "Password": new_password_entry, "Notes": new_notes}
        new_entry_json = json.dumps(new_entry_data)

        try:
            new_encrypted_data = self.encryption_handler.encrypt_data(self.current_master_key, new_entry_json)
        except Exception as e:
            logging.error(f"Encryption failed during update for entry ID {entry_id}: {e}")
            return False, f"Encryption failed during update: {e}"

        updated = self.db_manager.update_entry(entry_id, self.current_user_id, new_name, new_encrypted_data)
        if updated:
            return True, f"Entry ID {entry_id} updated successfully."
        else:
            return False, f"Failed to update entry ID {entry_id}. It may not exist or you may not have permission."

    def remove_entry(self, entry_id: int) -> Tuple[bool, str]:
        """Removes a password entry."""
        if not self.is_logged_in():
            return False, "No user logged in."

        deleted = self.db_manager.delete_entry(entry_id, self.current_user_id)
        if deleted:
            return True, f"Entry ID {entry_id} removed successfully."
        else:
            return False, f"Failed to remove entry ID {entry_id}. It may not exist or you may not have permission."

    def change_master_password(self, old_master_password: str, new_master_password: str) -> Tuple[bool, str]:
        """Changes the master password for the logged-in user."""
        if not self.is_logged_in():
            return False, "No user logged in."

        user_data = self._load_user_data(self.current_username)
        if not user_data:
             return False, "Could not load user data to verify password."
        
        _, stored_salt, stored_derived_key = user_data
        if self.encryption_handler.derive_key(old_master_password, stored_salt) != stored_derived_key:
             return False, "Incorrect current master password."

        strength_check = VerificationUtils.check_password_strength(new_master_password)
        if not strength_check['is_strong']:
            return False, "New master password is too weak. " + " ".join(strength_check['feedback'])

        if new_master_password == old_master_password:
            return False, "New master password cannot be the same as the old one."

        new_salt = self.encryption_handler.generate_salt()
        new_derived_key = self.encryption_handler.derive_key(new_master_password, new_salt)

        success, entries_or_error = self.view_entries()
        if not success:
            return False, f"Failed to retrieve entries for re-encryption: {entries_or_error}"

        if isinstance(entries_or_error, list):
            for entry_dict in entries_or_error:
                entry_id = entry_dict['id']
                entry_name = entry_dict['EntryName']
                original_content = {k: v for k, v in entry_dict.items() if k not in ['id', 'EntryName']}
                original_json = json.dumps(original_content)
                try:
                    re_encrypted_data = self.encryption_handler.encrypt_data(new_derived_key, original_json)
                    self.db_manager.update_entry(entry_id, self.current_user_id, entry_name, re_encrypted_data)
                except Exception as e:
                    logging.error(f"Error re-encrypting entry ID {entry_id} during master password change: {e}")
                    return False, f"Error re-encrypting entry ID {entry_id}. Aborted."

        updated_user = self.db_manager.update_user_master_key_details(self.current_user_id, new_salt, new_derived_key)
        if updated_user:
            self.current_master_key = new_derived_key
            return True, "Master password changed successfully. All entries have been re-encrypted."
        else:
            return False, "Failed to update master password in database."

    def generate_random_password(self, length: int, use_uppercase: bool, use_lowercase: bool, use_digits: bool, use_special_chars: bool) -> Tuple[bool, str]:
        """Generates a random password."""
        if not isinstance(length, int) or length <= 0:
            return False, "Password length must be a positive integer."

        if not any([use_uppercase, use_lowercase, use_digits, use_special_chars]):
            return False, "At least one character set must be selected."

        password = PasswordGenerator.generate_password(length, use_uppercase, use_lowercase, use_digits, use_special_chars)
        return (True, password) if password else (False, "Failed to generate password.")
