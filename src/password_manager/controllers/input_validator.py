"""
Input validation utilities for the Password Manager.
Provides centralized validation for all user inputs.
"""

from password_manager.utils.verification_utils import VerificationUtils

class InputValidator:
    """Centralized input validation for the application."""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username input."""
        if not username.strip():
            return False, "Username cannot be empty"
        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters long"
        if len(username.strip()) > 50:
            return False, "Username must be less than 50 characters long"
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password input."""
        if not password:
            return False, "Password cannot be empty"
        
        strength_info = VerificationUtils.check_password_strength(password)
        if not strength_info['is_strong']:
            weak_password_msg = "Weak password detected:\n"
            for feedback_msg in strength_info['feedback']:
                weak_password_msg += f"• {feedback_msg}\n"
            weak_password_msg += "\nPlease choose a stronger password."
            return False, weak_password_msg
        
        return True, ""
    
    @staticmethod
    def validate_password_confirmation(password: str, confirm_password: str) -> tuple[bool, str]:
        """Validate password confirmation."""
        if password != confirm_password:
            return False, "Passwords do not match"
        return True, ""
    
    @staticmethod
    def validate_entry_data(entry_data: dict) -> tuple[bool, str]:
        """Validate entry data."""
        name = entry_data.get('name', '').strip()
        password = entry_data.get('password', '')
        
        if not name:
            return False, "Entry name is required"
        if not password:
            return False, "Password is required"
        if len(name) > 100:
            return False, "Entry name must be less than 100 characters"
        
        return True, ""
    
    @staticmethod
    def validate_entry_fields(name: str, address: str, username_entry: str, 
                             password_entry: str, notes: str) -> tuple[bool, str]:
        """Validate all entry fields using verification utils."""
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
        return True, ""
    
    @staticmethod
    def validate_password_generation_params(length: int, use_uppercase: bool, 
                                          use_lowercase: bool, use_digits: bool, 
                                          use_special_chars: bool) -> tuple[bool, str]:
        """Validate password generation parameters."""
        if not isinstance(length, int) or length <= 0:
            return False, "Password length must be a positive integer"
        if length < 8:
            return False, "Password length must be at least 8 characters"
        if length > 64:
            return False, "Password length must be at most 64 characters"
        if not any([use_uppercase, use_lowercase, use_digits, use_special_chars]):
            return False, "At least one character set must be selected"
        return True, ""
    
    @staticmethod
    def validate_registration_inputs(username: str, password: str, confirm_password: str) -> dict:
        """Validate all registration inputs."""
        # Validate username
        username_valid, username_msg = InputValidator.validate_username(username)
        if not username_valid:
            return {'valid': False, 'message': username_msg}
        
        # Validate password
        password_valid, password_msg = InputValidator.validate_password(password)
        if not password_valid:
            return {'valid': False, 'message': password_msg}
        
        # Validate password confirmation
        confirm_valid, confirm_msg = InputValidator.validate_password_confirmation(password, confirm_password)
        if not confirm_valid:
            return {'valid': False, 'message': confirm_msg}
        
        return {'valid': True, 'message': ''}
    
    @staticmethod
    def validate_login_inputs(username: str, password: str) -> tuple[bool, str]:
        """Validate login inputs."""
        if not username.strip():
            return False, "Username is required"
        if not password:
            return False, "Password is required"
        return True, "" 