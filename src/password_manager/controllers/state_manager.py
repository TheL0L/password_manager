"""
Application state management for the Password Manager.
Handles centralized state management with observer pattern.
"""

import logging

class ApplicationState:
    """Centralized state management for the application."""
    
    def __init__(self):
        self._is_logged_in = False
        self._current_username: str | None = None
        self._current_entries: list[dict] = []
        self._observers: list[callable] = []
    
    @property
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in."""
        return self._is_logged_in
    
    @property
    def current_username(self) -> str | None:
        """Get the current username."""
        return self._current_username
    
    @property
    def current_entries(self) -> list[dict]:
        """Get a copy of current entries."""
        return self._current_entries.copy()
    
    def set_logged_in(self, username: str) -> None:
        """Set user as logged in."""
        self._is_logged_in = True
        self._current_username = username
        self._notify_observers()
    
    def set_logged_out(self) -> None:
        """Set user as logged out."""
        self._is_logged_in = False
        self._current_username = None
        self._current_entries = []
        self._notify_observers()
    
    def set_entries(self, entries: list[dict]) -> None:
        """Set current entries."""
        self._current_entries = entries.copy()
        self._notify_observers()
    
    def add_observer(self, observer: callable) -> None:
        """Add an observer to be notified of state changes."""
        self._observers.append(observer)
    
    def remove_observer(self, observer: callable) -> None:
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self) -> None:
        """Notify all observers of state changes."""
        for observer in self._observers:
            try:
                observer()
            except Exception as e:
                logging.error(f"Error notifying observer: {e}")
    
    def get_state_summary(self) -> dict:
        """Get a summary of the current state."""
        return {
            'is_logged_in': self._is_logged_in,
            'current_username': self._current_username,
            'entry_count': len(self._current_entries)
        } 