"""
Entry controller for the Password Manager.
Handles CRUD operations for password entries.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal
from password_manager.interfaces import ModelInterface
from password_manager.controllers.state_manager import ApplicationState
from password_manager.controllers.error_handler import ErrorHandler
from password_manager.controllers.input_validator import InputValidator

class EntryController(QObject):
    """Entry controller for password entry management."""
    
    entries_updated = pyqtSignal(list)
    entry_added = pyqtSignal(dict)
    entry_updated = pyqtSignal(dict)
    entry_deleted = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, model: ModelInterface, state: ApplicationState):
        """Initialize the entry controller.
        
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
    
    def load_entries(self) -> None:
        """Load all password entries for the current user."""
        try:
            if not self.model.is_logged_in():
                self.error_occurred.emit("No user logged in.")
                return
            
            success, entries_or_error = self.model.view_entries()
            if success:
                if isinstance(entries_or_error, list):
                    self.state.set_entries(entries_or_error)
                    self.entries_updated.emit(entries_or_error)
                    self.logger.info(f"Loaded {len(entries_or_error)} entries")
                else:
                    self.error_occurred.emit("Invalid data received for entries.")
            else:
                self.error_occurred.emit(str(entries_or_error))
                
        except Exception as e:
            error_msg = self.error_handler.handle_api_error("Load entries", e, self.logger)
            self.error_occurred.emit(error_msg)
    
    def add_entry(self, name: str, address: str, username_entry: str, 
                  password_entry: str, notes: str) -> None:
        """Add a new password entry."""
        try:
            if not self.model.is_logged_in():
                self.error_occurred.emit("No user logged in.")
                return
            
            # Validate entry data
            entry_data = {
                'name': name,
                'address': address,
                'username': username_entry,
                'password': password_entry,
                'notes': notes
            }
            entry_valid, entry_msg = self.validator.validate_entry_data(entry_data)
            if not entry_valid:
                self.error_occurred.emit(entry_msg)
                return
            
            success, message = self.model.add_entry(name, address, username_entry, password_entry, notes)
            if success:
                # Reload entries to get the new entry with ID
                self.load_entries()
                self.logger.info(f"Entry '{name}' added successfully")
            else:
                self.error_occurred.emit(message)
                self.logger.warning(f"Failed to add entry '{name}': {message}")
                
        except Exception as e:
            error_msg = self.error_handler.handle_api_error("Add entry", e, self.logger)
            self.error_occurred.emit(error_msg)
    
    def edit_entry(self, entry_id: int, name: str, address: str, username_entry: str,
                   password_entry: str, notes: str) -> None:
        """Edit an existing password entry."""
        try:
            if not self.model.is_logged_in():
                self.error_occurred.emit("No user logged in.")
                return
            
            # Validate entry data
            entry_data = {
                'name': name,
                'address': address,
                'username': username_entry,
                'password': password_entry,
                'notes': notes
            }
            entry_valid, entry_msg = self.validator.validate_entry_data(entry_data)
            if not entry_valid:
                self.error_occurred.emit(entry_msg)
                return
            
            success, message = self.model.edit_entry(entry_id, name, address, username_entry, password_entry, notes)
            if success:
                # Reload entries to get the updated entry
                self.load_entries()
                self.logger.info(f"Entry ID {entry_id} updated successfully")
            else:
                self.error_occurred.emit(message)
                self.logger.warning(f"Failed to update entry ID {entry_id}: {message}")
                
        except Exception as e:
            error_msg = self.error_handler.handle_api_error("Edit entry", e, self.logger)
            self.error_occurred.emit(error_msg)
    
    def delete_entry(self, entry_id: int) -> None:
        """Delete a password entry."""
        try:
            if not self.model.is_logged_in():
                self.error_occurred.emit("No user logged in.")
                return
            
            success, message = self.model.remove_entry(entry_id)
            if success:
                self.entry_deleted.emit(entry_id)
                # Reload entries to update the list
                self.load_entries()
                self.logger.info(f"Entry ID {entry_id} deleted successfully")
            else:
                self.error_occurred.emit(message)
                self.logger.warning(f"Failed to delete entry ID {entry_id}: {message}")
                
        except Exception as e:
            error_msg = self.error_handler.handle_api_error("Delete entry", e, self.logger)
            self.error_occurred.emit(error_msg)
    
    def get_entry_by_id(self, entry_id: int) -> dict | None:
        """Get an entry by its ID."""
        try:
            if not self.model.is_logged_in():
                return None
            
            success, entry_or_error = self.model.get_entry_by_id(entry_id)
            if success and isinstance(entry_or_error, dict):
                return entry_or_error
            else:
                self.logger.warning(f"Failed to get entry ID {entry_id}: {entry_or_error}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting entry ID {entry_id}: {e}")
            return None
    
    def get_current_entries(self) -> list[dict]:
        """Get the current entries from state."""
        return self.state.current_entries 