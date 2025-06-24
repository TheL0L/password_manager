import secrets
import string

class PasswordGenerator:
    """
    Generates strong, random passwords based on specified criteria.
    Uses the 'secrets' module for cryptographically strong random numbers.
    """

    # Define character sets
    LOWERCASE_CHARS = string.ascii_lowercase
    UPPERCASE_CHARS = string.ascii_uppercase
    DIGIT_CHARS = string.digits
    SPECIAL_CHARS = string.punctuation

    @staticmethod
    def generate_password(
        length: int,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special_chars: bool = True
    ) -> str | None:
        """
        Generates a random password.

        Args:
            length (int): The desired length of the password.
            use_uppercase (bool): Include uppercase letters.
            use_lowercase (bool): Include lowercase letters.
            use_digits (bool): Include digits.
            use_special_chars (bool): Include special characters.

        Returns:
            str | None: The generated password string, or None if no character sets
                        are selected or length is invalid.
        """
        if length <= 0:
            return None

        # Build the character pool based on selected options
        character_pool = ""
        if use_uppercase:
            character_pool += PasswordGenerator.UPPERCASE_CHARS
        if use_lowercase:
            character_pool += PasswordGenerator.LOWERCASE_CHARS
        if use_digits:
            character_pool += PasswordGenerator.DIGIT_CHARS
        if use_special_chars:
            character_pool += PasswordGenerator.SPECIAL_CHARS

        if not character_pool:
            return None

        # Ensure the password contains at least one character from each selected category
        password_chars = []
        if use_uppercase:
            password_chars.append(secrets.choice(PasswordGenerator.UPPERCASE_CHARS))
        if use_lowercase:
            password_chars.append(secrets.choice(PasswordGenerator.LOWERCASE_CHARS))
        if use_digits:
            password_chars.append(secrets.choice(PasswordGenerator.DIGIT_CHARS))
        if use_special_chars:
            password_chars.append(secrets.choice(PasswordGenerator.SPECIAL_CHARS))

        # Fill the remaining length with random characters from the full pool
        # Adjust length if initial guaranteed characters exceed it
        remaining_length = length - len(password_chars)
        if remaining_length < 0: # This can happen if length is too small for selected char types
            # If length is too small, just return the required characters
            return "".join(secrets.choice(character_pool) for _ in range(length))


        password_chars.extend(secrets.choice(character_pool) for _ in range(remaining_length))

        # Shuffle the characters to ensure randomness in position
        secrets.SystemRandom().shuffle(password_chars)

        return "".join(password_chars)
