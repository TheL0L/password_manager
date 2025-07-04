import pytest
from password_manager.utils.password_generator import PasswordGenerator

class TestPasswordGenerator:
    """
    Test suite for the PasswordGenerator class.
    """

    def test_generate_password_default_settings(self):
        """
        Tests password generation with default settings.
        The password should have the correct length and contain at least one of each required character type.
        """
        length = 16
        password = PasswordGenerator.generate_password(length)

        assert password is not None
        assert len(password) == length
        assert any(c in PasswordGenerator.LOWERCASE_CHARS for c in password)
        assert any(c in PasswordGenerator.UPPERCASE_CHARS for c in password)
        assert any(c in PasswordGenerator.DIGIT_CHARS for c in password)
        assert any(c in PasswordGenerator.SPECIAL_CHARS for c in password)

    def test_generate_password_custom_length(self):
        """
        Tests that the generated password has the specified custom length.
        """
        length = 32
        password = PasswordGenerator.generate_password(length)
        assert password is not None
        assert len(password) == length

    def test_generate_password_no_uppercase(self):
        """
        Tests password generation with uppercase characters excluded.
        """
        length = 20
        password = PasswordGenerator.generate_password(length, use_uppercase=False)
        assert password is not None
        assert not any(c in PasswordGenerator.UPPERCASE_CHARS for c in password)
        # It should still contain the other character types
        assert any(c in PasswordGenerator.LOWERCASE_CHARS for c in password)
        assert any(c in PasswordGenerator.DIGIT_CHARS for c in password)
        assert any(c in PasswordGenerator.SPECIAL_CHARS for c in password)

    def test_generate_password_only_digits(self):
        """
        Tests password generation with only digits.
        """
        length = 10
        password = PasswordGenerator.generate_password(
            length,
            use_uppercase=False,
            use_lowercase=False,
            use_special_chars=False
        )
        assert password is not None
        assert all(c in PasswordGenerator.DIGIT_CHARS for c in password)

    def test_generate_password_only_lowercase(self):
        """
        Tests password generation with only lowercase letters.
        """
        length = 15
        password = PasswordGenerator.generate_password(
            length,
            use_uppercase=False,
            use_digits=False,
            use_special_chars=False
        )
        assert password is not None
        assert all(c in PasswordGenerator.LOWERCASE_CHARS for c in password)

    def test_generate_password_all_options_false_returns_none(self):
        """
        Tests that generating a password with no selected character sets returns None.
        """
        password = PasswordGenerator.generate_password(
            12,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_special_chars=False
        )
        assert password is None

    def test_generate_password_zero_length_returns_none(self):
        """
        Tests that a requested length of 0 returns None.
        """
        password = PasswordGenerator.generate_password(0)
        assert password is None

    def test_generate_password_negative_length_returns_none(self):
        """
        Tests that a negative requested length returns None.
        """
        password = PasswordGenerator.generate_password(-5)
        assert password is None

    def test_generate_password_length_too_small_for_all_types(self):
        """
        Tests behavior when the requested length is smaller than the number of
        guaranteed character types. The implementation should still produce a
        password of the requested length from the available character pool.
        """
        length = 3
        password = PasswordGenerator.generate_password(length)  # Using 4 types by default
        assert password is not None
        assert len(password) == length

    @pytest.mark.parametrize("length", [8, 11, 16, 23, 32])
    def test_generate_password_is_not_none_for_valid_lengths(self, length):
        """
        Uses pytest's parametrize to test multiple valid lengths.
        """
        password = PasswordGenerator.generate_password(length)
        assert password is not None
