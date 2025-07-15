import pytest
from password_manager.utils.encryption_handler import EncryptionHandler
import os

class TestEncryptionHandler:
    """
    Test suite for the EncryptionHandler class.
    """

    def test_generate_salt(self):
        """
        Test that generate_salt produces a salt of the correct length
        and that it is random (different each time).
        """
        salt1 = EncryptionHandler.generate_salt()
        salt2 = EncryptionHandler.generate_salt()

        assert isinstance(salt1, bytes)
        assert len(salt1) == EncryptionHandler.SALT_LEN
        assert salt1 != salt2  # Check for randomness

    def test_derive_key(self):
        """
        Test that derive_key produces a key of the correct length
        and that the same password/salt combination produces the same key.
        """
        password = "test_password"
        salt = EncryptionHandler.generate_salt()

        key1 = EncryptionHandler.derive_key(password, salt)
        key2 = EncryptionHandler.derive_key(password, salt)

        assert isinstance(key1, bytes)
        assert len(key1) == EncryptionHandler.KEY_LENGTH
        assert key1 == key2  # Ensure deterministic derivation

        # Test with different password/salt to ensure different keys
        key3 = EncryptionHandler.derive_key("different_password", salt)
        key4 = EncryptionHandler.derive_key(password, EncryptionHandler.generate_salt())

        assert key1 != key3
        assert key1 != key4

    def test_encrypt_decrypt_data_success(self):
        """
        Test successful encryption and decryption of data.
        """
        password = "secure_password"
        salt = EncryptionHandler.generate_salt()
        key = EncryptionHandler.derive_key(password, salt)
        original_data = "This is a secret message."

        encrypted_data = EncryptionHandler.encrypt_data(key, original_data)
        decrypted_data = EncryptionHandler.decrypt_data(key, encrypted_data)

        assert isinstance(encrypted_data, bytes)
        assert encrypted_data != original_data.encode('utf-8') # Ensure it's actually encrypted
        assert decrypted_data == original_data

    def test_decrypt_data_with_wrong_key(self):
        """
        Test that decrypt_data returns None when an incorrect key is used.
        """
        password = "correct_password"
        salt = EncryptionHandler.generate_salt()
        key = EncryptionHandler.derive_key(password, salt)
        original_data = "Some sensitive data."
        encrypted_data = EncryptionHandler.encrypt_data(key, original_data)

        wrong_password = "wrong_password"
        wrong_key = EncryptionHandler.derive_key(wrong_password, salt)

        decrypted_data = EncryptionHandler.decrypt_data(wrong_key, encrypted_data)
        assert decrypted_data is None

    def test_decrypt_data_with_tampered_data(self):
        """
        Test that decrypt_data returns None when the encrypted data is tampered with.
        """
        password = "another_password"
        salt = EncryptionHandler.generate_salt()
        key = EncryptionHandler.derive_key(password, salt)
        original_data = "Data to be tampered."
        encrypted_data = EncryptionHandler.encrypt_data(key, original_data)

        # Tamper with the encrypted data
        tampered_data = encrypted_data[:-5] + b'abcde' # Change last 5 bytes

        decrypted_data = EncryptionHandler.decrypt_data(key, tampered_data)
        assert decrypted_data is None

    def test_encrypt_decrypt_empty_string(self):
        """
        Test encryption and decryption of an empty string.
        """
        password = "empty_test_password"
        salt = EncryptionHandler.generate_salt()
        key = EncryptionHandler.derive_key(password, salt)
        original_data = ""

        encrypted_data = EncryptionHandler.encrypt_data(key, original_data)
        decrypted_data = EncryptionHandler.decrypt_data(key, encrypted_data)

        assert decrypted_data == original_data

    def test_encrypt_decrypt_long_string(self):
        """
        Test encryption and decryption of a long string.
        """
        password = "long_string_password"
        salt = EncryptionHandler.generate_salt()
        key = EncryptionHandler.derive_key(password, salt)
        original_data = "a" * 1000 # A long string

        encrypted_data = EncryptionHandler.encrypt_data(key, original_data)
        decrypted_data = EncryptionHandler.decrypt_data(key, encrypted_data)

        assert decrypted_data == original_data

    def test_encrypt_data_raises_exception_on_invalid_key_length(self):
        """
        Test that encrypt_data raises an exception if the key length is not 32 bytes.
        Note: Fernet expects a 32-byte key. While derive_key ensures this,
        we test direct passing of an invalid key to encrypt_data.
        """
        # Create an intentionally wrong-sized key
        invalid_key = os.urandom(16) # 16 bytes instead of 32
        data = "some data"

        with pytest.raises(ValueError): # Fernet expects a 32-byte key
            EncryptionHandler.encrypt_data(invalid_key, data)

    def test_decrypt_data_fails_on_invalid_key_length(self):
        """
        Test that decrypt_data raises an exception if the key length is not 32 bytes.
        """
        invalid_key = os.urandom(16)
        encrypted_data = b"some_encrypted_bytes" # Dummy encrypted data

        # Fernet expects a 32-byte key
        assert EncryptionHandler.decrypt_data(invalid_key, encrypted_data) is None
    