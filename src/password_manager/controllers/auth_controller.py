"""
Authentication controller for the Password Manager.
Handles user registration, login, logout, and password changes.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal
from password_manager.interfaces import ModelInterface
from password_manager.controllers.state_manager import ApplicationState
from password_manager.controllers.error_handler import ErrorHandler
from password_manager.controllers.input_validator import InputValidator

class AuthController(QObject):
    """Authentication controller for user management."""
    
    login_successful = pyqtSignal(str)
    login_failed = pyqtSignal(str)
    logout_successful = pyqtSignal()
    registration_successful = pyqtSignal(str)
    registration_failed = pyqtSignal(str)
    master_password_changed = pyqtSignal()
    
    def __init__(self, model: ModelInterface, state: ApplicationState):
        """Initialize the authentication controller.
        
        Args:
            model: Model interface for API operations
            state: Application state manager
        """
        super().__init__()
        self.model = model
        self.state = state
        self.error_handler = ErrorHandler()
        self.validator = InputValidator()
        self.logger = logging.getLogger(__name__)
    
    def register_user(self, username: str, password: str, confirm_password: str) -> None:
        """Register a new user."""
        try:
            # Validate inputs
            validation_result = self.validator.validate_registration_inputs(username, password, confirm_password)
            if not validation_result['valid']:
                self.registration_failed.emit(validation_result['message'])
                return
            
            # Attempt registration
            success, message = self.model.register_user(username, password)
            if success:
                self.registration_successful.emit(username)
                self.logger.info(f"User '{username}' registered successfully")
            else:
                self.registration_failed.emit(message)
                self.logger.warning(f"Registration failed for '{username}': {message}")
                
        except Exception as e:
            error_msg = self.error_handler.handle_api_error("Registration", e, self.logger)
            self.registration_failed.emit(error_msg)
    
    def login_user(self, username: str, password: str) -> None:
        """Login a user."""
        try:
            # Validate inputs
            valid, msg = self.validator.validate_login_inputs(username, password)
            if not valid:
                error_msg = self.error_handler.handle_validation_error("Login", msg)
                self.login_failed.emit(error_msg)
                return
            
            success, message = self.model.login_user(username, password)
            if success:
                self.state.set_logged_in(username)
                self.login_successful.emit(username)
                self.logger.info(f"User '{username}' logged in successfully")
            else:
                error_msg = self.error_handler.handle_authentication_error(message)
                self.login_failed.emit(error_msg)
                self.logger.warning(f"Login failed for '{username}': {message}")
                
        except Exception as e:
            error_msg = self.error_handler.handle_api_error("Login", e, self.logger)
            self.login_failed.emit(error_msg)
    
    def logout_user(self) -> None:
        """Logout the current user."""
        try:
            success, message = self.model.logout_user()
            if success:
                self.state.set_logged_out()
                self.logout_successful.emit()
                self.logger.info("User logged out successfully")
            else:
                self.logger.warning(f"Logout error: {message}")
                
        except Exception as e:
            error_msg = self.error_handler.handle_api_error("Logout", e, self.logger)
            self.logger.error(error_msg)
    
    def change_master_password(self, old_password: str, new_password: str, confirm_new_password: str) -> None:
        """Change the master password."""
        try:
            # Validate inputs
            if not old_password or not new_password or not confirm_new_password:
                self.logger.error("All password fields are required for password change")
                return
            
            # Validate new password
            password_valid, password_msg = self.validator.validate_password(new_password)
            if not password_valid:
                self.logger.error(f"New password validation failed: {password_msg}")
                return
            
            # Validate password confirmation
            confirm_valid, confirm_msg = self.validator.validate_password_confirmation(new_password, confirm_new_password)
            if not confirm_valid:
                self.logger.error(f"Password confirmation failed: {confirm_msg}")
                return
            
            success, message = self.model.change_master_password(old_password, new_password)
            if success:
                self.master_password_changed.emit()
                self.logger.info("Master password changed successfully")
            else:
                self.logger.warning(f"Failed to change master password: {message}")
                
        except Exception as e:
            error_msg = self.error_handler.handle_api_error("Change master password", e, self.logger)
            self.logger.error(error_msg)
    
    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self.state.is_logged_in
    
    def get_current_username(self) -> str | None:
        """Get the current username."""
        return self.state.current_username 