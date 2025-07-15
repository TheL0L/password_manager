"""
Password controller for the Password Manager.
Handles password generation, validation, and strength checking.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal
from password_manager.utils.password_generator import PasswordGenerator
from password_manager.utils.verification_utils import VerificationUtils
from password_manager.controllers.input_validator import InputValidator

class PasswordController(QObject):
    """Password controller for password-related operations."""
    
    password_generated = pyqtSignal(str)
    password_strength_updated = pyqtSignal(dict)
    
    def __init__(self):
        """Initialize the password controller."""
        super().__init__()
        self.validator = InputValidator()
        self.logger = logging.getLogger(__name__)
    
    def generate_password(self, length: int, use_uppercase: bool = True, 
                         use_lowercase: bool = True, use_digits: bool = True, 
                         use_special_chars: bool = True, exclude_similar: bool = False,
                         exclude_ambiguous: bool = False) -> str:
        """Generate a password with the specified parameters."""
        try:
            # Validate parameters
            valid, msg = self.validator.validate_password_generation_params(
                length, use_uppercase, use_lowercase, use_digits, use_special_chars
            )
            if not valid:
                self.logger.error(f"Password generation validation failed: {msg}")
                return ""
            
            # If exclusions are requested, we need to generate a longer password
            # to account for characters that will be removed
            adjusted_length = length
            if exclude_similar or exclude_ambiguous:
                # Increase length to compensate for excluded characters
                adjusted_length = int(length * 1.5)
            
            # Generate password using the utility class
            password = PasswordGenerator.generate_password(
                adjusted_length, use_uppercase, use_lowercase, use_digits, use_special_chars
            )
            
            if password:
                # Apply additional filters if requested
                if exclude_similar:
                    password = self._exclude_similar_characters(password)
                if exclude_ambiguous:
                    password = self._exclude_ambiguous_characters(password)
                
                # Ensure the final password meets the minimum length requirement
                # If it's too short, generate a new one
                if len(password) < length:
                    # Try generating again with a longer length
                    retry_length = int(length * 2)
                    retry_password = PasswordGenerator.generate_password(
                        retry_length, use_uppercase, use_lowercase, use_digits, use_special_chars
                    )
                    if retry_password:
                        if exclude_similar:
                            retry_password = self._exclude_similar_characters(retry_password)
                        if exclude_ambiguous:
                            retry_password = self._exclude_ambiguous_characters(retry_password)
                        
                        # Take the first 'length' characters
                        password = retry_password[:length]
                
                # Ensure we don't exceed the requested length
                if len(password) > length:
                    password = password[:length]
                
                self.password_generated.emit(password)
                self.logger.info(f"Generated password of length {len(password)}")
                return password
            else:
                self.logger.error("Failed to generate password")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error generating password: {e}")
            return ""
    
    def check_password_strength(self, password: str) -> dict:
        """Check password strength and return detailed feedback."""
        try:
            strength_info = VerificationUtils.check_password_strength(password)
            self.password_strength_updated.emit(strength_info)
            return strength_info
        except Exception as e:
            self.logger.error(f"Error checking password strength: {e}")
            return {
                'is_strong': False,
                'score': 0,
                'feedback': ['Error checking password strength']
            }
    
    def _exclude_similar_characters(self, password: str) -> str:
        """Exclude similar characters from password."""
        similar_chars = "l1IO0"
        return ''.join(c for c in password if c not in similar_chars)
    
    def _exclude_ambiguous_characters(self, password: str) -> str:
        """Exclude ambiguous characters from password."""
        ambiguous_chars = "{}[]()/\\|`~"
        return ''.join(c for c in password if c not in ambiguous_chars)
    