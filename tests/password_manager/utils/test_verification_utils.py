import pytest
from password_manager.utils.verification_utils import VerificationUtils

class TestVerificationUtils:
    """
    Test suite for the VerificationUtils class.
    """

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
