"""
Main controller for the Password Manager GUI application.
Coordinates between specialized controllers and the view.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal
from password_manager.password_manager_api import PasswordManagerAPI
from password_manager.interfaces import ViewInterface, ModelInterface
from password_manager.controllers.state_manager import ApplicationState
from password_manager.controllers.auth_controller import AuthController
from password_manager.controllers.entry_controller import EntryController
from password_manager.controllers.password_controller import PasswordController

class MainController(QObject):
    """Main controller that coordinates specialized controllers."""
    
    login_successful = pyqtSignal(str)
    login_failed = pyqtSignal(str)
    logout_successful = pyqtSignal()
    registration_successful = pyqtSignal(str)
    registration_failed = pyqtSignal(str)
    entries_updated = pyqtSignal(list)
    entry_added = pyqtSignal(dict)
    entry_updated = pyqtSignal(dict)
    entry_deleted = pyqtSignal(int)
    password_generated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    master_password_changed = pyqtSignal()
    
    def __init__(self, view: ViewInterface, model: ModelInterface | None = None):
        """Initialize the main controller.
        
        Args:
            view: View interface for loose coupling
            model: Model interface (optional, creates default if not provided)
        """
        super().__init__()
        self.view = view
        self.model = model or PasswordManagerAPI()
        self.state = ApplicationState()
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized controllers
        self._init_controllers()
        
        # Connect signals to UI slots
        self._connect_signals()
        
        # Add state observer
        self.state.add_observer(self._on_state_changed)
    
    def _init_controllers(self):
        """Initialize specialized controllers."""
        self.auth_controller = AuthController(self.model, self.state)
        self.entry_controller = EntryController(self.model, self.state)
        self.password_controller = PasswordController()
    
    def _connect_signals(self):
        """Connect controller signals to UI slots."""
        # Connect auth controller signals
        self.auth_controller.login_successful.connect(self.view.on_login_successful)
        self.auth_controller.login_failed.connect(self.view.on_login_failed)
        self.auth_controller.logout_successful.connect(self.view.on_logout_successful)
        self.auth_controller.registration_successful.connect(self.view.on_registration_successful)
        self.auth_controller.registration_failed.connect(self.view.on_registration_failed)
        self.auth_controller.master_password_changed.connect(self.view.on_master_password_changed)
        
        # Connect entry controller signals
        self.entry_controller.entries_updated.connect(self.view.on_entries_updated)
        self.entry_controller.entry_added.connect(self.view.on_entry_added)
        self.entry_controller.entry_updated.connect(self.view.on_entry_updated)
        self.entry_controller.entry_deleted.connect(self.view.on_entry_deleted)
        self.entry_controller.error_occurred.connect(self.view.on_error_occurred)
        
        # Connect password controller signals
        self.password_controller.password_generated.connect(self.view.on_password_generated)
        self.password_controller.password_strength_updated.connect(self._on_password_strength_updated)
        
        # Forward signals to main controller for external access
        self.auth_controller.login_successful.connect(self.login_successful.emit)
        self.auth_controller.login_failed.connect(self.login_failed.emit)
        self.auth_controller.logout_successful.connect(self.logout_successful.emit)
        self.auth_controller.registration_successful.connect(self.registration_successful.emit)
        self.auth_controller.registration_failed.connect(self.registration_failed.emit)
        self.auth_controller.master_password_changed.connect(self.master_password_changed.emit)
        
        self.entry_controller.entries_updated.connect(self.entries_updated.emit)
        self.entry_controller.entry_added.connect(self.entry_added.emit)
        self.entry_controller.entry_updated.connect(self.entry_updated.emit)
        self.entry_controller.entry_deleted.connect(self.entry_deleted.emit)
        self.entry_controller.error_occurred.connect(self.error_occurred.emit)
        
        self.password_controller.password_generated.connect(self.password_generated.emit)
    
    def _on_state_changed(self):
        """Handle state changes."""
        self.logger.debug(f"Application state changed - Logged in: {self.state.is_logged_in}, "
                         f"User: {self.state.current_username}, Entries: {len(self.state.current_entries)}")
    
    def _on_password_strength_updated(self, strength_info: dict):
        """Handle password strength updates."""
        # This can be used for logging or other purposes
        self.logger.debug(f"Password strength updated: {strength_info}")
    
    # Authentication methods (delegated to auth controller)
    def register_user(self, username: str, password: str, confirm_password: str) -> None:
        """Register a new user."""
        self.auth_controller.register_user(username, password, confirm_password)
    
    def login_user(self, username: str, password: str) -> None:
        """Login a user."""
        self.auth_controller.login_user(username, password)
        # Load entries after successful login
        if self.auth_controller.is_logged_in():
            self.entry_controller.load_entries()
    
    def logout_user(self) -> None:
        """Logout the current user."""
        self.auth_controller.logout_user()
    
    def change_master_password(self, old_password: str, new_password: str, confirm_new_password: str) -> None:
        """Change the master password."""
        self.auth_controller.change_master_password(old_password, new_password, confirm_new_password)
    
    # Entry management methods (delegated to entry controller)
    def load_entries(self) -> None:
        """Load all password entries for the current user."""
        self.entry_controller.load_entries()
    
    def add_entry(self, name: str, address: str, username_entry: str, 
                  password_entry: str, notes: str) -> None:
        """Add a new password entry."""
        self.entry_controller.add_entry(name, address, username_entry, password_entry, notes)
    
    def edit_entry(self, entry_id: int, name: str, address: str, username_entry: str,
                   password_entry: str, notes: str) -> None:
        """Edit an existing password entry."""
        self.entry_controller.edit_entry(entry_id, name, address, username_entry, password_entry, notes)
    
    def delete_entry(self, entry_id: int) -> None:
        """Delete a password entry."""
        self.entry_controller.delete_entry(entry_id)
    
    def get_entry_by_id(self, entry_id: int):
        """Get an entry by its ID."""
        return self.entry_controller.get_entry_by_id(entry_id)
    
    # Password generation method delegated to password controller
    def generate_password(self, length: int = 16, use_uppercase: bool = True,
                         use_lowercase: bool = True, use_digits: bool = True,
                         use_special_chars: bool = True, exclude_similar: bool = False,
                         exclude_ambiguous: bool = False) -> str:
        """Generate a password with the specified parameters."""
        return self.password_controller.generate_password(
            length, use_uppercase, use_lowercase, use_digits, use_special_chars,
            exclude_similar, exclude_ambiguous
        )
    
    def check_password_strength(self, password: str) -> dict:
        """Check password strength and return detailed feedback."""
        return self.password_controller.check_password_strength(password)
    
    # State access methods
    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self.state.is_logged_in
    
    def get_current_username(self):
        """Get the current username."""
        return self.state.current_username
    
    def get_current_entries(self):
        """Get the current entries."""
        return self.state.current_entries 