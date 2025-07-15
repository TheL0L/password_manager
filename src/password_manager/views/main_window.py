"""
Main window for the Password Manager GUI application.
"""

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
    QStatusBar, QApplication, QMessageBox
)
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QAction

from password_manager.views.auth_widget import AuthWidget
from password_manager.views.dashboard_widget import DashboardWidget
from password_manager.views.entry_dialog import EntryDialog
from password_manager.views.password_generator_dialog import PasswordGeneratorDialog
from password_manager.views.change_password_dialog import ChangePasswordDialog

class MainWindow(QMainWindow):
    """Main window for the password manager application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.controller = None  # Will be set by the controller
        self.current_entries = []
        self.current_username = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # Start with authentication view
        self.show_auth_view()
    
    def setup_ui(self):
        """Setup the main UI components."""
        self.setWindowTitle("Password Manager")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Center the window on screen
        self.center_window()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create views
        self.auth_widget = AuthWidget()
        self.dashboard_widget = DashboardWidget()
        
        # Add views to stacked widget
        self.stacked_widget.addWidget(self.auth_widget)
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        # Connect signals
        self._connect_signals()
    
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # User menu (initially hidden, shown after login)
        self.user_menu = menubar.addMenu("&User")
        self.user_menu.setVisible(False)
        
        # Change password action
        self.change_password_action = QAction("&Change Password", self)
        self.change_password_action.setShortcut("Ctrl+P")
        self.change_password_action.setStatusTip("Change master password")
        self.change_password_action.triggered.connect(self._on_change_password_requested)
        self.change_password_action.setEnabled(False)
        self.user_menu.addAction(self.change_password_action)
        
        # Logout action
        self.logout_action = QAction("&Logout", self)
        self.logout_action.setShortcut("Ctrl+L")
        self.logout_action.setStatusTip("Logout from the application")
        self.logout_action.triggered.connect(self._on_logout_requested)
        self.logout_action.setEnabled(False) 
        self.user_menu.addAction(self.logout_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Password generator action
        generator_action = QAction("&Password Generator", self)
        generator_action.setShortcut("Ctrl+G")
        generator_action.setStatusTip("Open password generator")
        generator_action.triggered.connect(self.show_password_generator)
        tools_menu.addAction(generator_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Password Manager")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def center_window(self):
        """Center the window on the screen."""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _connect_signals(self):
        """Connect signals from child widgets."""
        # Auth widget signals
        self.auth_widget.login_requested.connect(self._on_login_requested)
        self.auth_widget.register_requested.connect(self._on_register_requested)
        
        # Dashboard widget signals
        self.dashboard_widget.add_entry_requested.connect(self._on_add_entry_requested)
        self.dashboard_widget.edit_entry_requested.connect(self._on_edit_entry_requested)
        self.dashboard_widget.delete_entry_requested.connect(self._on_delete_entry_requested)
        self.dashboard_widget.view_entry_requested.connect(self._on_view_entry_requested)
        self.dashboard_widget.generate_password_requested.connect(self._on_generate_password_requested)
    
    def set_controller(self, controller):
        """Set the controller reference."""
        self.controller = controller
    
    def show_auth_view(self):
        """Show the authentication view."""
        self.stacked_widget.setCurrentWidget(self.auth_widget)
        self.status_bar.showMessage("Please login or register")
        # Hide user menu when showing auth view
        self.user_menu.setVisible(False)
        # Disable user menu actions to prevent keyboard shortcuts when logged out
        self.change_password_action.setEnabled(False)
        self.logout_action.setEnabled(False)
        # Clear any stored state
        self.current_username = None
        self.current_entries = []
    
    def show_dashboard_view(self):
        """Show the dashboard view."""
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.status_bar.showMessage(f"Welcome, {self.current_username or 'User'}!")
        # Show user menu when showing dashboard view
        self.user_menu.setVisible(True)
        # Enable user menu actions to allow keyboard shortcuts when logged in
        self.change_password_action.setEnabled(True)
        self.logout_action.setEnabled(True)
    
    # Signal handlers for auth widget
    def _on_login_requested(self, username: str, password: str):
        """Handle login request from auth widget."""
        if self.controller:
            self.controller.login_user(username, password)
    
    def _on_register_requested(self, username: str, password: str, confirm_password: str):
        """Handle registration request from auth widget."""
        if self.controller:
            self.controller.register_user(username, password, confirm_password)
    
    # Signal handlers for dashboard widget
    def _on_add_entry_requested(self):
        """Handle add entry request from dashboard."""
        dialog = EntryDialog(self)
        if dialog.exec() == EntryDialog.DialogCode.Accepted:
            entry_data = dialog.get_entry_data()
            if self.controller:
                self.controller.add_entry(**entry_data)
    
    def _on_edit_entry_requested(self, entry_id: int):
        """Handle edit entry request from dashboard."""
        if self.controller:
            entry = self.controller.get_entry_by_id(entry_id)
            if entry:
                dialog = EntryDialog(self, entry)
                if dialog.exec() == EntryDialog.DialogCode.Accepted:
                    entry_data = dialog.get_entry_data()
                    self.controller.edit_entry(entry_id, **entry_data)
            else:
                self._show_error_message("Entry not found", "The selected entry could not be found.")
    
    def _on_delete_entry_requested(self, entry_id: int):
        """Handle delete entry request from dashboard."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this entry? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes and self.controller:
            self.controller.delete_entry(entry_id)
    
    def _on_view_entry_requested(self, entry_id: int):
        """Handle view entry request from dashboard."""
        if self.controller:
            entry = self.controller.get_entry_by_id(entry_id)
            if entry:
                self._show_entry_details(entry)
            else:
                self._show_error_message("Entry not found", "The selected entry could not be found.")
    
    def _on_logout_requested(self):
        """Handle logout request from menu."""
        # Additional security check - ensure user is logged in
        if not self.controller or not self.controller.is_logged_in():
            self._show_error_message("Authentication Required", "You must be logged in to logout.")
            return
            
        if self.controller:
            self.controller.logout_user()
    
    def _on_change_password_requested(self):
        """Handle change password request from menu."""
        # Additional security check - ensure user is logged in
        if not self.controller or not self.controller.is_logged_in():
            self._show_error_message("Authentication Required", "You must be logged in to change your password.")
            return
            
        dialog = ChangePasswordDialog(self)
        if dialog.exec() == ChangePasswordDialog.DialogCode.Accepted:
            old_password, new_password, confirm_password = dialog.get_passwords()
            if self.controller:
                self.controller.change_master_password(old_password, new_password, confirm_password)
    
    def _on_generate_password_requested(self):
        """Handle generate password request from dashboard."""
        self.show_password_generator()
    
    def show_password_generator(self):
        """Show the password generator dialog."""
        dialog = PasswordGeneratorDialog(self)
        dialog.exec()
    
    def _show_entry_details(self, entry: dict):
        """Show entry details in a message box."""
        details = f"""
Entry Details:
Name: {entry.get('Name', 'N/A')}
Website/URL: {entry.get('Address', 'N/A')}
Username: {entry.get('Username', 'N/A')}
Password: {'*' * len(entry.get('Password', ''))}
Notes: {entry.get('Notes', 'N/A')}
        """.strip()
        
        QMessageBox.information(self, "Entry Details", details)
    
    def _show_error_message(self, title: str, message: str):
        """Show an error message to the user."""
        QMessageBox.critical(self, title, message)
    
    def show_about(self):
        """Show the about dialog."""
        about_text = """
Password Manager v1.0.0

A secure password management application built with PyQt6.

Features:
• Secure password storage with encryption
• Password generation
• User authentication
• Entry management

Built with Python and PyQt6.
        """.strip()
        
        QMessageBox.about(self, "About Password Manager", about_text)
    
    # ViewInterface implementation methods
    @pyqtSlot(str)
    def on_login_successful(self, username: str):
        """Handle successful login."""
        self.current_username = username
        self.show_dashboard_view()
        self.auth_widget.clear_fields()
        self.logger.info(f"User '{username}' logged in successfully")
    
    @pyqtSlot(str)
    def on_login_failed(self, error_message: str):
        """Handle failed login."""
        self._show_error_message("Login Failed", error_message)
        self.auth_widget.set_login_focus()
        self.logger.warning(f"Login failed: {error_message}")
    
    @pyqtSlot()
    def on_logout_successful(self):
        """Handle successful logout."""
        self.show_auth_view()
        self.auth_widget.set_login_focus()
        self.logger.info("User logged out successfully")
    
    @pyqtSlot(str)
    def on_registration_successful(self, username: str):
        """Handle successful registration."""
        QMessageBox.information(
            self,
            "Registration Successful",
            f"User '{username}' registered successfully. You can now login."
        )
        self.auth_widget.set_login_focus()
        self.logger.info(f"User '{username}' registered successfully")
    
    @pyqtSlot(str)
    def on_registration_failed(self, error_message: str):
        """Handle failed registration."""
        self._show_error_message("Registration Failed", error_message)
        self.auth_widget.set_register_focus()
        self.logger.warning(f"Registration failed: {error_message}")
    
    @pyqtSlot(list)
    def on_entries_updated(self, entries: list[dict]):
        """Handle entries update."""
        self.current_entries = entries
        self.dashboard_widget.update_entries(entries)
        self.status_bar.showMessage(f"Loaded {len(entries)} entries")
        self.logger.info(f"Updated {len(entries)} entries")
    
    @pyqtSlot(dict)
    def on_entry_added(self, entry: dict):
        """Handle entry added."""
        self.status_bar.showMessage(f"Entry '{entry.get('Name', 'Unknown')}' added successfully", 3000)
        self.logger.info(f"Entry '{entry.get('Name', 'Unknown')}' added")
    
    @pyqtSlot(dict)
    def on_entry_updated(self, entry: dict):
        """Handle entry updated."""
        self.status_bar.showMessage(f"Entry '{entry.get('Name', 'Unknown')}' updated successfully", 3000)
        self.logger.info(f"Entry '{entry.get('Name', 'Unknown')}' updated")
    
    @pyqtSlot(int)
    def on_entry_deleted(self, entry_id: int):
        """Handle entry deleted."""
        self.status_bar.showMessage("Entry deleted successfully", 3000)
        self.logger.info(f"Entry ID {entry_id} deleted")
    
    @pyqtSlot(str)
    def on_password_generated(self, password: str):
        """Handle password generated."""
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(password)
        self.status_bar.showMessage("Password generated and copied to clipboard", 3000)
        self.logger.info("Password generated and copied to clipboard")
    
    @pyqtSlot(str)
    def on_error_occurred(self, error_message: str):
        """Handle general error."""
        self._show_error_message("Error", error_message)
        self.logger.error(f"Error occurred: {error_message}")
    
    @pyqtSlot()
    def on_master_password_changed(self):
        """Handle master password changed."""
        QMessageBox.information(
            self,
            "Password Changed",
            "Master password changed successfully."
        )
        self.logger.info("Master password changed successfully")
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.controller and self.controller.is_logged_in():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "You are currently logged in. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.logger.info("Application closed by user")
                event.accept()
            else:
                event.ignore()
        else:
            self.logger.info("Application closed by user")
            event.accept() 