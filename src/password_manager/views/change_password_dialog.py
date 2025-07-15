"""
Change password dialog for updating the master password.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from password_manager.controllers.password_controller import PasswordController

class ChangePasswordDialog(QDialog):
    """Dialog for changing the master password."""
    
    def __init__(self, parent=None):
        """Initialize the change password dialog."""
        super().__init__(parent)
        self.password_controller = PasswordController()
        self.setup_ui()
        self._connect_signals()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Change Master Password")
        self.setMinimumSize(400, 300)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Password fields
        self._create_password_fields(main_layout)
        
        # Password strength indicator
        self._create_strength_indicator(main_layout)
        
        # Buttons
        self._create_buttons(main_layout)
    
    def _create_password_fields(self, parent_layout):
        """Create the password input fields."""
        fields_group = QGroupBox("Password Information")
        fields_layout = QGridLayout(fields_group)
        fields_layout.setSpacing(10)
        
        # Current password
        current_label = QLabel("Current Password:")
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setPlaceholderText("Enter your current master password")
        self.current_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_edit.setMinimumHeight(30)
        fields_layout.addWidget(current_label, 0, 0)
        fields_layout.addWidget(self.current_password_edit, 0, 1)
        
        # New password
        new_label = QLabel("New Password:")
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setPlaceholderText("Enter your new master password")
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_edit.setMinimumHeight(30)
        fields_layout.addWidget(new_label, 1, 0)
        fields_layout.addWidget(self.new_password_edit, 1, 1)
        
        # Confirm new password
        confirm_label = QLabel("Confirm New Password:")
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Confirm your new master password")
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setMinimumHeight(30)
        fields_layout.addWidget(confirm_label, 2, 0)
        fields_layout.addWidget(self.confirm_password_edit, 2, 1)
        
        # Show passwords checkbox
        self.show_passwords_checkbox = QCheckBox("Show passwords")
        self.show_passwords_checkbox.toggled.connect(self._toggle_password_visibility)
        fields_layout.addWidget(self.show_passwords_checkbox, 3, 1)
        
        parent_layout.addWidget(fields_group)
    
    def _create_strength_indicator(self, parent_layout):
        """Create the password strength indicator."""
        strength_group = QGroupBox("Password Strength")
        strength_layout = QVBoxLayout(strength_group)
        
        self.strength_label = QLabel("Password strength: ")
        self.strength_label.setStyleSheet("color: #666; font-size: 10px;")
        strength_layout.addWidget(self.strength_label)
        
        # Password requirements
        requirements_label = QLabel("Requirements:")
        requirements_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        strength_layout.addWidget(requirements_label)
        
        self.requirements_text = QLabel(
            "• At least 8 characters long\n"
            "• Contains uppercase letters\n"
            "• Contains lowercase letters\n"
            "• Contains numbers\n"
            "• Contains special characters"
        )
        self.requirements_text.setStyleSheet("color: #666; font-size: 9px; margin-left: 10px;")
        strength_layout.addWidget(self.requirements_text)
        
        parent_layout.addWidget(strength_group)
    
    def _create_buttons(self, parent_layout):
        """Create the button section."""
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
        
        # Change password button
        self.change_button = QPushButton("Change Password")
        self.change_button.setMinimumHeight(35)
        self.change_button.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b91d47;
            }
        """)
        button_layout.addWidget(self.change_button)
        
        parent_layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Button signals
        self.change_button.clicked.connect(self._on_change_clicked)
        self.cancel_button.clicked.connect(self.reject)
        
        # Password field signals
        self.new_password_edit.textChanged.connect(self._update_password_strength)
        self.confirm_password_edit.textChanged.connect(self._update_password_strength)
        
        # Enter key in confirm field triggers change
        self.confirm_password_edit.returnPressed.connect(self._on_change_clicked)
    
    def _toggle_password_visibility(self, checked: bool):
        """Toggle password visibility."""
        if checked:
            self.current_password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.current_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _update_password_strength(self):
        """Update password strength indicator using the controller."""
        password = self.new_password_edit.text()
        if not password:
            self.strength_label.setText("Password strength: ")
            self.strength_label.setStyleSheet("color: #666; font-size: 10px;")
            self.requirements_text.setText(
                "• At least 8 characters long\n"
                "• Contains uppercase letters\n"
                "• Contains lowercase letters\n"
                "• Contains numbers\n"
                "• Contains special characters"
            )
            self.requirements_text.setStyleSheet("color: #666; font-size: 9px; margin-left: 10px;")
            return
        
        # Use the password controller to check strength
        strength_info = self.password_controller.check_password_strength(password)
        
        # Update strength label
        if strength_info['is_strong']:
            strength_text = "Strong"
            color = "#107c10"
        else:
            # Determine strength level based on score
            score = strength_info.get('score', 0)
            if score <= 2:
                strength_text = "Weak"
                color = "#d13438"
            elif score <= 3:
                strength_text = "Fair"
                color = "#ff8c00"
            else:
                strength_text = "Good"
                color = "#ffb900"
        
        self.strength_label.setText(f"Password strength: {strength_text}")
        self.strength_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
        
        # Update requirements text
        feedback = strength_info.get('feedback', [])
        if feedback:
            requirements_text = "Missing:\n" + "\n".join(f"• {req}" for req in feedback)
            self.requirements_text.setText(requirements_text)
            self.requirements_text.setStyleSheet("color: #d13438; font-size: 9px; margin-left: 10px;")
        else:
            self.requirements_text.setText("All requirements met ✓")
            self.requirements_text.setStyleSheet("color: #107c10; font-size: 9px; margin-left: 10px; font-weight: bold;")
    
    def _on_change_clicked(self):
        """Handle change password button click."""
        # Validate inputs
        current_password = self.current_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        if not current_password:
            QMessageBox.warning(self, "Validation Error", "Please enter your current password.")
            self.current_password_edit.setFocus()
            return
        
        if not new_password:
            QMessageBox.warning(self, "Validation Error", "Please enter a new password.")
            self.new_password_edit.setFocus()
            return
        
        if not confirm_password:
            QMessageBox.warning(self, "Validation Error", "Please confirm your new password.")
            self.confirm_password_edit.setFocus()
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Validation Error", "New passwords do not match.")
            self.confirm_password_edit.setFocus()
            return
        
        # Check password strength
        strength_info = self.password_controller.check_password_strength(new_password)
        if not strength_info['is_strong']:
            QMessageBox.warning(self, "Weak Password", 
                              "Please choose a stronger password that meets all requirements.")
            self.new_password_edit.setFocus()
            return
        
        # Accept the dialog
        self.accept()
    
    def get_passwords(self) -> tuple:
        """Get the password values from the dialog.
        
        Returns:
            Tuple of (current_password, new_password, confirm_password)
        """
        return (
            self.current_password_edit.text(),
            self.new_password_edit.text(),
            self.confirm_password_edit.text()
        ) 