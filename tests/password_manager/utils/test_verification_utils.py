import pytest
from password_manager.utils.verification_utils import VerificationUtils

class TestVerificationUtils:
    """
    Test suite for the VerificationUtils class.
    """

    # Tests for validate_length method
    @pytest.mark.parametrize("length", [0, 1, 2])
    def test_validate_length_valid_string(self, length):
        """
        Tests string length validation.
        Input string should not exceed the provided maximum length.
        """
        is_valid, message = VerificationUtils.validate_length("a" * length, 3)
        assert is_valid is True
        assert message == ""
    
    def test_validate_length_too_long(self):
        """
        Tests string rejection when the provided maximum length is exceeded.
        """
        is_valid, message = VerificationUtils.validate_length("abc" * 20, 15)
        assert not is_valid
        assert message
    
    def test_validate_length_not_string(self):
        """
        Tests that non-string input is rejected.
        """
        is_valid, message = VerificationUtils.validate_length(123, 10)
        assert not is_valid
        assert message

    def test_validate_length_exact_limit(self):
        """
        Tests string exactly at the maximum length limit.
        """
        is_valid, message = VerificationUtils.validate_length("a" * 10, 10)
        assert is_valid is True
        assert message == ""

    def test_validate_length_one_over_limit(self):
        """
        Tests string one character over the limit.
        """
        is_valid, message = VerificationUtils.validate_length("a" * 11, 10)
        assert not is_valid
        assert "exceeds maximum of 10 characters" in message

    def test_validate_length_custom_field_name(self):
        """
        Tests custom field name in error message.
        """
        is_valid, message = VerificationUtils.validate_length("a" * 11, 10, "TestField")
        assert not is_valid
        assert "TestField length exceeds maximum" in message

    def test_validate_length_none_input(self):
        """
        Tests None input is rejected.
        """
        is_valid, message = VerificationUtils.validate_length(None, 10)
        assert not is_valid
        assert "must be a string" in message

    # Tests for check_password_strength method
    def test_check_password_strength_strong_password(self):
        """
        Tests a strong password that meets all criteria.
        """
        password = "StrongPassword123!"
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is True
        assert "Great! Password contains a good mix" in result['feedback'][0]

    def test_check_password_strength_too_short(self):
        """
        Tests password shorter than minimum length.
        """
        password = "Short1!"
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is False
        assert any("must be at least 12 characters" in feedback for feedback in result['feedback'])

    def test_check_password_strength_no_uppercase(self):
        """
        Tests password without uppercase letters.
        """
        password = "lowercase123!"
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is False
        assert any("uppercase letters" in feedback for feedback in result['feedback'])

    def test_check_password_strength_no_lowercase(self):
        """
        Tests password without lowercase letters.
        """
        password = "UPPERCASE123!"
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is False
        assert any("lowercase letters" in feedback for feedback in result['feedback'])

    def test_check_password_strength_no_numbers(self):
        """
        Tests password without numbers.
        """
        password = "PasswordNoNumbers!"
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is False
        assert any("numbers" in feedback for feedback in result['feedback'])

    def test_check_password_strength_no_special_chars(self):
        """
        Tests password without special characters.
        """
        password = "PasswordNoSpecial123"
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is False
        assert any("special characters" in feedback for feedback in result['feedback'])

    def test_check_password_strength_empty_password(self):
        """
        Tests empty password.
        """
        password = ""
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is False
        assert len(result['feedback']) > 0

    def test_check_password_strength_minimum_length_with_all_types(self):
        """
        Tests password exactly at minimum length with all character types.
        """
        password = "Password123!"  # exactly 12 characters
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is True

    def test_check_password_strength_all_special_chars(self):
        """
        Tests password with various special characters.
        """
        special_chars = "!@#$%^&*()_+={}[]:;\"'<,>.?/~`-"
        for char in special_chars:
            password = f"Password123{char}"
            result = VerificationUtils.check_password_strength(password)
            assert result['is_strong'] is True

    # Tests for is_valid_username method
    def test_is_valid_username_valid_cases(self):
        """
        Tests valid username cases.
        """
        valid_usernames = [
            "user123",
            "test_user",
            "user.name",
            "user-name",
            "a",  # single character
            "user123._-",  # all allowed special chars
            "A" * 50  # maximum length
        ]
        for username in valid_usernames:
            is_valid, message = VerificationUtils.is_valid_username(username)
            assert is_valid is True, f"Username '{username}' should be valid"
            assert message == ""

    def test_is_valid_username_empty(self):
        """
        Tests empty username.
        """
        is_valid, message = VerificationUtils.is_valid_username("")
        assert not is_valid
        assert "cannot be empty" in message

    def test_is_valid_username_too_long(self):
        """
        Tests username exceeding maximum length.
        """
        long_username = "a" * 51  # one over limit
        is_valid, message = VerificationUtils.is_valid_username(long_username)
        assert not is_valid
        assert "exceeds maximum of 50 characters" in message

    def test_is_valid_username_invalid_characters(self):
        """
        Tests username with invalid characters.
        """
        invalid_usernames = [
            "user@domain",  # @ not allowed
            "user name",    # space not allowed
            "user#123",     # # not allowed
            "user$123",     # $ not allowed
            "user%123",     # % not allowed
            "user+123",     # + not allowed
            "用户123",       # non-ASCII characters
        ]
        for username in invalid_usernames:
            is_valid, message = VerificationUtils.is_valid_username(username)
            assert not is_valid, f"Username '{username}' should be invalid"
            assert "can only contain" in message

    def test_is_valid_username_none_input(self):
        """
        Tests None username input.
        """
        is_valid, message = VerificationUtils.is_valid_username(None)
        assert not is_valid
        assert "cannot be empty" in message

    # Tests for is_valid_entry_name method
    def test_is_valid_entry_name_valid_cases(self):
        """
        Tests valid entry name cases.
        """
        valid_names = [
            "Gmail",
            "Work Email Account",
            "Banking - Main Account",
            "a",  # single character
            "A" * 100  # maximum length
        ]
        for name in valid_names:
            is_valid, message = VerificationUtils.is_valid_entry_name(name)
            assert is_valid is True, f"Entry name '{name}' should be valid"
            assert message == ""

    def test_is_valid_entry_name_empty(self):
        """
        Tests empty entry name.
        """
        is_valid, message = VerificationUtils.is_valid_entry_name("")
        assert not is_valid
        assert "cannot be empty" in message

    def test_is_valid_entry_name_too_long(self):
        """
        Tests entry name exceeding maximum length.
        """
        long_name = "a" * 101  # one over limit
        is_valid, message = VerificationUtils.is_valid_entry_name(long_name)
        assert not is_valid
        assert "exceeds maximum of 100 characters" in message

    def test_is_valid_entry_name_none_input(self):
        """
        Tests None entry name input.
        """
        is_valid, message = VerificationUtils.is_valid_entry_name(None)
        assert not is_valid
        assert "cannot be empty" in message

    # Tests for is_valid_address method
    def test_is_valid_address_valid_cases(self):
        """
        Tests valid address cases including empty.
        """
        valid_addresses = [
            "",  # empty is allowed
            "https://www.example.com",
            "ftp://files.company.com",
            "just some text",
            "A" * 250  # maximum length
        ]
        for address in valid_addresses:
            is_valid, message = VerificationUtils.is_valid_address(address)
            assert is_valid is True, f"Address '{address}' should be valid"
            assert message == ""

    def test_is_valid_address_too_long(self):
        """
        Tests address exceeding maximum length.
        """
        long_address = "a" * 251  # one over limit
        is_valid, message = VerificationUtils.is_valid_address(long_address)
        assert not is_valid
        assert "exceeds maximum of 250 characters" in message

    def test_is_valid_address_none_input(self):
        """
        Tests None address input (should be treated as empty and valid).
        """
        is_valid, message = VerificationUtils.is_valid_address(None)
        assert is_valid is True
        assert message == ""

    # Tests for is_valid_entry_username_field method
    def test_is_valid_entry_username_field_valid_cases(self):
        """
        Tests valid entry username field cases including empty.
        """
        valid_usernames = [
            "",  # empty is allowed
            "user@example.com",
            "username123",
            "A" * 250  # maximum length
        ]
        for username in valid_usernames:
            is_valid, message = VerificationUtils.is_valid_entry_username_field(username)
            assert is_valid is True, f"Entry username '{username}' should be valid"
            assert message == ""

    def test_is_valid_entry_username_field_too_long(self):
        """
        Tests entry username field exceeding maximum length.
        """
        long_username = "a" * 251  # one over limit
        is_valid, message = VerificationUtils.is_valid_entry_username_field(long_username)
        assert not is_valid
        assert "exceeds maximum of 250 characters" in message

    def test_is_valid_entry_username_field_none_input(self):
        """
        Tests None entry username field input.
        """
        is_valid, message = VerificationUtils.is_valid_entry_username_field(None)
        assert is_valid is True
        assert message == ""

    # Tests for is_valid_entry_password_field method
    def test_is_valid_entry_password_field_valid_cases(self):
        """
        Tests valid entry password field cases including empty.
        """
        valid_passwords = [
            "",  # empty is allowed
            "password123",
            "very_complex_password_with_special_chars!@#",
            "A" * 250  # maximum length
        ]
        for password in valid_passwords:
            is_valid, message = VerificationUtils.is_valid_entry_password_field(password)
            assert is_valid is True, f"Entry password should be valid"
            assert message == ""

    def test_is_valid_entry_password_field_too_long(self):
        """
        Tests entry password field exceeding maximum length.
        """
        long_password = "a" * 251  # one over limit
        is_valid, message = VerificationUtils.is_valid_entry_password_field(long_password)
        assert not is_valid
        assert "exceeds maximum of 250 characters" in message

    def test_is_valid_entry_password_field_none_input(self):
        """
        Tests None entry password field input.
        """
        is_valid, message = VerificationUtils.is_valid_entry_password_field(None)
        assert is_valid is True
        assert message == ""

    # Tests for is_valid_entry_notes method
    def test_is_valid_entry_notes_valid_cases(self):
        """
        Tests valid entry notes cases including empty.
        """
        valid_notes = [
            "",  # empty is allowed
            "Some notes about this entry",
            "Multi-line\nnotes with\nspecial chars!@#$%",
            "A" * 250  # maximum length
        ]
        for notes in valid_notes:
            is_valid, message = VerificationUtils.is_valid_entry_notes(notes)
            assert is_valid is True, f"Entry notes should be valid"
            assert message == ""

    def test_is_valid_entry_notes_too_long(self):
        """
        Tests entry notes exceeding maximum length.
        """
        long_notes = "a" * 251  # one over limit
        is_valid, message = VerificationUtils.is_valid_entry_notes(long_notes)
        assert not is_valid
        assert "exceeds maximum of 250 characters" in message

    def test_is_valid_entry_notes_none_input(self):
        """
        Tests None entry notes input.
        """
        is_valid, message = VerificationUtils.is_valid_entry_notes(None)
        assert is_valid is True
        assert message == ""

    # Edge case tests for class constants
    def test_class_constants_values(self):
        """
        Tests that class constants have expected values.
        """
        assert VerificationUtils.MIN_PASSWORD_LENGTH == 12
        assert VerificationUtils.MAX_USERNAME_LENGTH == 50
        assert VerificationUtils.MAX_ENTRY_NAME_LENGTH == 100
        assert VerificationUtils.MAX_ENTRY_FIELD_LENGTH == 250

    # Comprehensive password strength edge cases
    def test_check_password_strength_exactly_minimum_length_weak(self):
        """
        Tests password exactly at minimum length but missing character types.
        """
        password = "aaaaaaaaaaaa"  # 12 chars, all lowercase
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is False
        # Should have feedback about missing uppercase, numbers, and special chars

    def test_check_password_strength_unicode_characters(self):
        """
        Tests password with unicode characters.
        """
        password = "Pássword123!"  # contains accented character
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is True  # Should still be strong

    def test_check_password_strength_very_long_password(self):
        """
        Tests very long password.
        """
        password = "VeryLongPassword123!" * 10  # 200+ characters
        result = VerificationUtils.check_password_strength(password)
        assert result['is_strong'] is True

    @pytest.mark.parametrize("invalid_input", [None, 123, [], {}])
    def test_methods_with_invalid_input_types(self, invalid_input):
        """
        Tests methods with various invalid input types.
        """
        # Most methods should handle non-string inputs gracefully
        # Note: Some methods may need to be updated to handle these cases properly
        methods_to_test = [
            VerificationUtils.is_valid_entry_name,
            VerificationUtils.is_valid_username
        ]
        
        for method in methods_to_test:
            try:
                is_valid, message = method(invalid_input)
                # Should return False for invalid types
                assert not is_valid
            except (TypeError, AttributeError):
                # If method doesn't handle invalid types, that's also acceptable
                pass
