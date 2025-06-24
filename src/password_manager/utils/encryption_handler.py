import os
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

class EncryptionHandler:
    """
    Handles key derivation using Argon2id from the cryptography library and
    symmetric encryption/decryption of data using Fernet (built on AES).
    """

    # Argon2id parameters
    TIME_COST = 3
    MEMORY_COST_MiB = 64
    PARALLELISM_DEGREE = 2
    KEY_LENGTH = 32  # For Fernet key
    SALT_LEN = 16

    def __init__(self):
        """
        Initializes the EncryptionHandler.
        """
        pass

    @staticmethod
    def generate_salt() -> bytes:
        """
        Generates a random salt of a specified length.

        Returns:
            bytes: A randomly generated salt.
        """
        return os.urandom(EncryptionHandler.SALT_LEN)

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Derives a cryptographic key from a password and salt using Argon2id.

        Args:
            password (str): The master password string.
            salt (bytes): The salt bytes.

        Returns:
            bytes: The derived key (32 bytes for Fernet).
        """
        kdf = Argon2id(
            salt=salt,
            iterations=EncryptionHandler.TIME_COST,
            memory_cost=EncryptionHandler.MEMORY_COST_MiB * 1024,  # The amount of memory to use in kibibytes
            lanes=EncryptionHandler.PARALLELISM_DEGREE,
            length=EncryptionHandler.KEY_LENGTH
        )
        key = kdf.derive(password.encode('utf-8'))
        return key

    @staticmethod
    def encrypt_data(key: bytes, data: str) -> bytes:
        """
        Encrypts a string of data using a derived key.

        The key must be 32 bytes long and url-safe base64 encoded for Fernet.
        The data string will be encoded to UTF-8 bytes before encryption.

        Args:
            key (bytes): The 32-byte derived key.
            data (str): The string data to be encrypted.

        Returns:
            bytes: The encrypted data.
        """
        try:
            # Fernet key needs to be URL-safe base64 encoded
            fernet_key = urlsafe_b64encode(key)
            f = Fernet(fernet_key)
            encrypted_data = f.encrypt(data.encode('utf-8'))
            return encrypted_data
        except Exception:
            # Re-raise the exception, allow the calling layer to handle logging/message
            raise

    @staticmethod
    def decrypt_data(key: bytes, encrypted_data: bytes) -> str | None:
        """
        Decrypts bytes of data using a derived key.

        The key must be 32 bytes long and url-safe base64 encoded for Fernet.
        The decrypted bytes will be decoded to a UTF-8 string.

        Args:
            key (bytes): The 32-byte derived key.
            encrypted_data (bytes): The encrypted data bytes.

        Returns:
            str | None: The decrypted string data, or None if decryption fails.
        """
        try:
            # Fernet key needs to be URL-safe base64 encoded
            fernet_key = urlsafe_b64encode(key)
            f = Fernet(fernet_key)
            decrypted_data = f.decrypt(encrypted_data).decode('utf-8')
            return decrypted_data
        except (InvalidToken, Exception):
            # Return None to be handled by the API layer
            return None
