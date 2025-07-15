"""
Entry dialog for adding and editing password entries.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from password_manager.controllers.input_validator import InputValidator

class EntryDialog(QDialog):
    """Dialog for adding or editing password entries."""
    
    def __init__(self, parent=None, entry: dict | None = None):
        """Initialize the entry dialog.
        
        Args:
            parent: Parent widget
            entry: Existing entry data for editing (None for new entry)
        """
        super().__init__(parent)
        self.entry = entry
        self.is_editing = entry is not None
        self.validator = InputValidator()
        
        self.setup_ui()
        self._connect_signals()
        
        if self.is_editing:
            self._populate_fields()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Edit Entry" if self.is_editing else "➕Add New Entry")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Entry details group
        details_group = QGroupBox("Entry Details")
        details_layout = QGridLayout(details_group)
        details_layout.setSpacing(10)
        
        # Name field
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Google, GitHub, Bank Account")
        self.name_edit.setMinimumHeight(30)
        details_layout.addWidget(name_label, 0, 0)
        details_layout.addWidget(self.name_edit, 0, 1)
        
        # Address field
        address_label = QLabel("Website/URL:")
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("e.g., https://google.com")
        self.address_edit.setMinimumHeight(30)
        details_layout.addWidget(address_label, 1, 0)
        details_layout.addWidget(self.address_edit, 1, 1)
        
        # Username field
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Your username for this service")
        self.username_edit.setMinimumHeight(30)
        details_layout.addWidget(username_label, 2, 0)
        details_layout.addWidget(self.username_edit, 2, 1)
        
        # Password field
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Your password for this service")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(30)
        details_layout.addWidget(password_label, 3, 0)
        details_layout.addWidget(self.password_edit, 3, 1)
        
        # Show password checkbox
        self.show_password_checkbox = QCheckBox("Show password")
        self.show_password_checkbox.toggled.connect(self._toggle_password_visibility)
        details_layout.addWidget(self.show_password_checkbox, 4, 1)
        
        # Notes field
        notes_label = QLabel("Notes:")
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Additional notes (optional)")
        self.notes_edit.setMaximumHeight(80)
        details_layout.addWidget(notes_label, 5, 0)
        details_layout.addWidget(self.notes_edit, 5, 1)
        
        main_layout.addWidget(details_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        # Save button
        self.save_button = QPushButton("Save" if self.is_editing else "Add Entry")
        self.save_button.setMinimumHeight(35)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0e6e0e;
            }
        """)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.save_button.clicked.connect(self._on_save_clicked)
        self.cancel_button.clicked.connect(self.reject)
        
        # Enter key in password field triggers save
        self.password_edit.returnPressed.connect(self._on_save_clicked)
    
    def _toggle_password_visibility(self, checked: bool):
        """Toggle password visibility."""
        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _populate_fields(self):
        """Populate fields with existing entry data."""
        if not self.entry:
            return
        
        self.name_edit.setText(self.entry.get('Name', ''))
        self.address_edit.setText(self.entry.get('Address', ''))
        self.username_edit.setText(self.entry.get('Username', ''))
        self.password_edit.setText(self.entry.get('Password', ''))
        self.notes_edit.setPlainText(self.entry.get('Notes', ''))
    
    def _on_save_clicked(self):
        """Handle save button click."""
        # Get form data
        name = self.name_edit.text().strip()
        address = self.address_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        notes = self.notes_edit.toPlainText().strip()
        
        # Validate using the controller
        valid, msg = self.validator.validate_entry_fields(name, address, username, password, notes)
        if not valid:
            QMessageBox.warning(self, "Validation Error", msg)
            # Set focus to the appropriate field based on the error
            if "name" in msg.lower():
                self.name_edit.setFocus()
            elif "password" in msg.lower():
                self.password_edit.setFocus()
            elif "username" in msg.lower():
                self.username_edit.setFocus()
            elif "address" in msg.lower():
                self.address_edit.setFocus()
            elif "notes" in msg.lower():
                self.notes_edit.setFocus()
            return
        
        # Accept the dialog
        self.accept()
    
    def get_entry_data(self) -> dict:
        """Get the entry data from the form fields.
        
        Returns:
            Dictionary containing the entry data
        """
        return {
            'name': self.name_edit.text().strip(),
            'address': self.address_edit.text().strip(),
            'username_entry': self.username_edit.text().strip(),
            'password_entry': self.password_edit.text(),
            'notes': self.notes_edit.toPlainText().strip()
        } 