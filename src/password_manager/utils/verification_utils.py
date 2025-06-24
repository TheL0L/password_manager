import re

class VerificationUtils:
    """
    Provides utility functions for verifying password strength,
    validating input lengths, and other common data validations.
    """

    # Constants for validation
    MIN_PASSWORD_LENGTH = 12
    MAX_USERNAME_LENGTH = 50
    MAX_ENTRY_NAME_LENGTH = 100
    MAX_ENTRY_FIELD_LENGTH = 250

    @staticmethod
    def check_password_strength(password: str) -> dict:
        """
        Evaluates the strength of a password based on several criteria.

        Args:
            password (str): The password string to evaluate.

        Returns:
            dict: A dictionary containing 'is_strong' (bool) and 'feedback' (list).
        """
        feedback = []
        is_strong = True

        if len(password) < VerificationUtils.MIN_PASSWORD_LENGTH:
            feedback.append(f"Password must be at least {VerificationUtils.MIN_PASSWORD_LENGTH} characters long.")
            is_strong = False

        checks = {
            "uppercase letters": r'[A-Z]',
            "lowercase letters": r'[a-z]',
            "numbers": r'\d',
            "special characters": r'[!@#$%^&*()_+={}\[\]:;"\'<,>.?/~`\-]'
        }

        for check_name, pattern in checks.items():
            if not re.search(pattern, password):
                feedback.append(f"Password should include {check_name}.")
                is_strong = False

        if is_strong:
            feedback.insert(0, "Great! Password contains a good mix of character types and is long enough.")

        return {'is_strong': is_strong, 'feedback': feedback}

    @staticmethod
    def validate_length(data: str, max_length: int, field_name: str = "Field") -> tuple[bool, str]:
        """
        Validates the length of a string.
        """
        if not isinstance(data, str):
            return False, f"{field_name} must be a string."
        if len(data) > max_length:
            return False, f"{field_name} length exceeds maximum of {max_length} characters."
        return True, ""

    @staticmethod
    def is_valid_username(username: str) -> tuple[bool, str]:
        """
        Validates the username.
        """
        if not username:
            return False, "Username cannot be empty."
        valid, msg = VerificationUtils.validate_length(username, VerificationUtils.MAX_USERNAME_LENGTH, "Username")
        if not valid:
            return valid, msg
        if not re.fullmatch(r'^[a-zA-Z0-9._-]+$', username):
            return False, "Username can only contain letters, numbers, and . _ -"
        return True, ""

    @staticmethod
    def is_valid_entry_name(entry_name: str) -> tuple[bool, str]:
        """
        Validates the entry name.
        """
        if not entry_name:
            return False, "Entry Name cannot be empty."
        return VerificationUtils.validate_length(entry_name, VerificationUtils.MAX_ENTRY_NAME_LENGTH, "Entry Name")

    @staticmethod
    def is_valid_address(address: str) -> tuple[bool, str]:
        """
        Validates the address field for an entry. Allows empty.
        """
        if not address:
            return True, ""
        return VerificationUtils.validate_length(address, VerificationUtils.MAX_ENTRY_FIELD_LENGTH, "Address")

    @staticmethod
    def is_valid_entry_username_field(username_field: str) -> tuple[bool, str]:
        """
        Validates the username field for an entry. Allows empty.
        """
        if not username_field:
            return True, ""
        return VerificationUtils.validate_length(username_field, VerificationUtils.MAX_ENTRY_FIELD_LENGTH, "Entry Username")

    @staticmethod
    def is_valid_entry_password_field(password_field: str) -> tuple[bool, str]:
        """
        Validates the password field for an entry. Allows empty.
        """
        if not password_field:
            return True, ""
        return VerificationUtils.validate_length(password_field, VerificationUtils.MAX_ENTRY_FIELD_LENGTH, "Entry Password")

    @staticmethod
    def is_valid_entry_notes(notes: str) -> tuple[bool, str]:
        """
        Validates the notes field for an entry. Allows empty.
        """
        if not notes:
            return True, ""
        return VerificationUtils.validate_length(notes, VerificationUtils.MAX_ENTRY_FIELD_LENGTH, "Entry Notes")
