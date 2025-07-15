"""
Password generator dialog for creating secure random passwords.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QSpinBox, QSlider, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from password_manager.controllers.password_controller import PasswordController

class PasswordGeneratorDialog(QDialog):
    """Dialog for generating secure random passwords."""
    
    def __init__(self, parent=None):
        """Initialize the password generator dialog."""
        super().__init__(parent)
        self.password_controller = PasswordController()
        self.setup_ui()
        self._connect_signals()
        self._update_password_preview()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Password Generator")
        self.setMinimumSize(450, 350)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Generated password display
        self._create_password_display(main_layout)
        
        # Password options
        self._create_password_options(main_layout)
        
        # Character options
        self._create_character_options(main_layout)
        
        # Buttons
        self._create_buttons(main_layout)
    
    def _create_password_display(self, parent_layout):
        """Create the password display section."""
        display_group = QGroupBox("Generated Password")
        display_layout = QVBoxLayout(display_group)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setReadOnly(True)
        self.password_edit.setMinimumHeight(40)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                color: #000;
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        display_layout.addWidget(self.password_edit)
        
        # Generate button
        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        
        self.generate_button = QPushButton("Generate New Password")
        self.generate_button.setMinimumHeight(30)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0e6e0e;
            }
        """)
        copy_layout.addWidget(self.generate_button)
        
        display_layout.addLayout(copy_layout)
        parent_layout.addWidget(display_group)
    
    def _create_password_options(self, parent_layout):
        """Create the password options section."""
        options_group = QGroupBox("Password Options")
        options_layout = QGridLayout(options_group)
        options_layout.setSpacing(10)
        
        # Length slider
        length_label = QLabel("Length:")
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(64)
        self.length_slider.setValue(16)
        self.length_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.length_slider.setTickInterval(8)
        
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setMinimum(8)
        self.length_spinbox.setMaximum(64)
        self.length_spinbox.setValue(16)
        
        options_layout.addWidget(length_label, 0, 0)
        options_layout.addWidget(self.length_slider, 0, 1)
        options_layout.addWidget(self.length_spinbox, 0, 2)
        
        # Length value label
        self.length_value_label = QLabel("16 characters")
        self.length_value_label.setStyleSheet("color: #666; font-size: 10px;")
        options_layout.addWidget(self.length_value_label, 1, 1)
        
        parent_layout.addWidget(options_group)
    
    def _create_character_options(self, parent_layout):
        """Create the character options section."""
        chars_group = QGroupBox("Character Types")
        chars_layout = QVBoxLayout(chars_group)
        chars_layout.setSpacing(8)
        
        # Uppercase letters
        self.uppercase_checkbox = QCheckBox("Uppercase letters (A-Z)")
        self.uppercase_checkbox.setChecked(True)
        chars_layout.addWidget(self.uppercase_checkbox)
        
        # Lowercase letters
        self.lowercase_checkbox = QCheckBox("Lowercase letters (a-z)")
        self.lowercase_checkbox.setChecked(True)
        chars_layout.addWidget(self.lowercase_checkbox)
        
        # Digits
        self.digits_checkbox = QCheckBox("Digits (0-9)")
        self.digits_checkbox.setChecked(True)
        chars_layout.addWidget(self.digits_checkbox)
        
        # Special characters
        self.special_checkbox = QCheckBox("Special characters (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        self.special_checkbox.setChecked(True)
        chars_layout.addWidget(self.special_checkbox)
        
        # Exclude similar characters
        self.exclude_similar_checkbox = QCheckBox("Exclude similar characters (l, 1, I, O, 0)")
        chars_layout.addWidget(self.exclude_similar_checkbox)
        
        # Exclude ambiguous characters
        self.exclude_ambiguous_checkbox = QCheckBox("Exclude ambiguous characters ({}, [], (), /, \\, |, `, ~)")
        chars_layout.addWidget(self.exclude_ambiguous_checkbox)
        
        parent_layout.addWidget(chars_group)
    
    def _create_buttons(self, parent_layout):
        """Create the button section."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.setMinimumHeight(35)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        button_layout.addWidget(self.copy_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setMinimumHeight(35)
        self.close_button.setStyleSheet("""
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
        button_layout.addWidget(self.close_button)
        
        parent_layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Button signals
        self.generate_button.clicked.connect(self._on_generate_clicked)
        self.copy_button.clicked.connect(self._on_copy_clicked)
        self.close_button.clicked.connect(self.accept)
        
        # Length controls
        self.length_slider.valueChanged.connect(self._on_length_changed)
        self.length_spinbox.valueChanged.connect(self._on_length_changed)
        
        # Character option changes
        self.uppercase_checkbox.toggled.connect(self._on_options_changed)
        self.lowercase_checkbox.toggled.connect(self._on_options_changed)
        self.digits_checkbox.toggled.connect(self._on_options_changed)
        self.special_checkbox.toggled.connect(self._on_options_changed)
    
    def _on_length_changed(self, value):
        """Handle length value changes."""
        self.length_slider.setValue(value)
        self.length_spinbox.setValue(value)
        self.length_value_label.setText(f"{value} characters")
        self._update_password_preview()
    
    def _on_options_changed(self):
        """Handle character option changes."""
        self._update_password_preview()
    
    def _update_password_preview(self):
        """Update the password preview."""
        # Check if at least one character type is selected
        if not any([
            self.uppercase_checkbox.isChecked(),
            self.lowercase_checkbox.isChecked(),
            self.digits_checkbox.isChecked(),
            self.special_checkbox.isChecked()
        ]):
            self.password_edit.setText("Please select at least one character type")
            return
        
        # Generate a preview password using the controller
        preview_password = self.password_controller.generate_password(
            length=self.length_spinbox.value(),
            use_uppercase=self.uppercase_checkbox.isChecked(),
            use_lowercase=self.lowercase_checkbox.isChecked(),
            use_digits=self.digits_checkbox.isChecked(),
            use_special_chars=self.special_checkbox.isChecked(),
            exclude_similar=self.exclude_similar_checkbox.isChecked(),
            exclude_ambiguous=self.exclude_ambiguous_checkbox.isChecked()
        )
        
        if preview_password:
            self.password_edit.setText(preview_password)
        else:
            self.password_edit.setText("No valid characters selected")
    
    def _on_generate_clicked(self):
        """Handle generate button click."""
        self._update_password_preview()
    
    def _on_copy_clicked(self):
        """Handle copy button click."""
        password = self.password_edit.text()
        if password and password != "Please select at least one character type" and password != "No valid characters selected":
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            QMessageBox.information(self, "Copied", "Password copied to clipboard!")
        else:
            QMessageBox.warning(self, "Copy Error", "No valid password to copy.")
    
    def get_generator_params(self) -> dict:
        """Get the current generator parameters.
        
        Returns:
            Dictionary containing the generator parameters
        """
        return {
            'length': self.length_spinbox.value(),
            'use_uppercase': self.uppercase_checkbox.isChecked(),
            'use_lowercase': self.lowercase_checkbox.isChecked(),
            'use_digits': self.digits_checkbox.isChecked(),
            'use_special_chars': self.special_checkbox.isChecked()
        } 