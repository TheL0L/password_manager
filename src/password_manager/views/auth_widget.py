"""
Authentication widget for login and registration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QGroupBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from password_manager.controllers.password_controller import PasswordController

class AuthWidget(QWidget):
    """Authentication widget with login and registration tabs."""
    
    login_requested = pyqtSignal(str, str)
    register_requested = pyqtSignal(str, str, str)
    
    def __init__(self):
        """Initialize the authentication widget."""
        super().__init__()
        self.password_controller = PasswordController()
        self.setup_ui()
        self._connect_signals()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Password Manager")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Secure Password Management")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        main_layout.addWidget(subtitle_label)
        
        # Tab widget for login/register
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.login_tab = self._create_login_tab()
        self.register_tab = self._create_register_tab()
        
        self.tab_widget.addTab(self.login_tab, "Login")
        self.tab_widget.addTab(self.register_tab, "Register")
        
        # Add some spacing
        main_layout.addStretch()
    
    def _create_login_tab(self) -> QWidget:
        """Create the login tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Login group
        login_group = QGroupBox("Login to Your Account")
        login_layout = QGridLayout(login_group)
        login_layout.setSpacing(15)
        
        # Username
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.setMinimumHeight(35)
        login_layout.addWidget(username_label, 0, 0)
        login_layout.addWidget(self.username_edit, 0, 1)
        
        # Password
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(35)
        login_layout.addWidget(password_label, 1, 0)
        login_layout.addWidget(self.password_edit, 1, 1)
        
        # Show password checkbox
        self.show_password_checkbox = QCheckBox("Show password")
        self.show_password_checkbox.toggled.connect(self._toggle_password_visibility)
        login_layout.addWidget(self.show_password_checkbox, 2, 1)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        login_layout.addWidget(self.login_button, 3, 0, 1, 2)
        
        layout.addWidget(login_group)
        layout.addStretch()
        
        return tab
    
    def _create_register_tab(self) -> QWidget:
        """Create the registration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Register group
        register_group = QGroupBox("Create New Account")
        register_layout = QGridLayout(register_group)
        register_layout.setSpacing(15)
        
        # Username
        reg_username_label = QLabel("Username:")
        self.reg_username_edit = QLineEdit()
        self.reg_username_edit.setPlaceholderText("Choose a username")
        self.reg_username_edit.setMinimumHeight(35)
        register_layout.addWidget(reg_username_label, 0, 0)
        register_layout.addWidget(self.reg_username_edit, 0, 1)
        
        # Password
        reg_password_label = QLabel("Password:")
        self.reg_password_edit = QLineEdit()
        self.reg_password_edit.setPlaceholderText("Choose a strong password")
        self.reg_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password_edit.setMinimumHeight(35)
        register_layout.addWidget(reg_password_label, 1, 0)
        register_layout.addWidget(self.reg_password_edit, 1, 1)
        
        # Confirm Password
        reg_confirm_label = QLabel("Confirm Password:")
        self.reg_confirm_edit = QLineEdit()
        self.reg_confirm_edit.setPlaceholderText("Confirm your password")
        self.reg_confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_confirm_edit.setMinimumHeight(35)
        register_layout.addWidget(reg_confirm_label, 2, 0)
        register_layout.addWidget(self.reg_confirm_edit, 2, 1)
        
        # Show password checkbox
        self.reg_show_password_checkbox = QCheckBox("Show passwords")
        self.reg_show_password_checkbox.toggled.connect(self._toggle_register_password_visibility)
        register_layout.addWidget(self.reg_show_password_checkbox, 3, 1)
        
        # Password strength indicator
        self.password_strength_label = QLabel("Password strength: ")
        self.password_strength_label.setStyleSheet("color: #666; font-size: 10px;")
        register_layout.addWidget(self.password_strength_label, 4, 0, 1, 2)
        
        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.setMinimumHeight(40)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0e6e0e;
            }
            QPushButton:pressed {
                background-color: #0c5c0c;
            }
        """)
        register_layout.addWidget(self.register_button, 5, 0, 1, 2)
        
        layout.addWidget(register_group)
        layout.addStretch()
        
        return tab
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Login signals
        self.login_button.clicked.connect(self._on_login_clicked)
        self.password_edit.returnPressed.connect(self._on_login_clicked)
        
        # Register signals
        self.register_button.clicked.connect(self._on_register_clicked)
        self.reg_confirm_edit.returnPressed.connect(self._on_register_clicked)
        
        # Password strength monitoring
        self.reg_password_edit.textChanged.connect(self._update_password_strength)
    
    def _toggle_password_visibility(self, checked: bool):
        """Toggle password visibility in login tab."""
        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _toggle_register_password_visibility(self, checked: bool):
        """Toggle password visibility in register tab."""
        if checked:
            self.reg_password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.reg_confirm_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.reg_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.reg_confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _update_password_strength(self):
        """Update password strength indicator using the controller."""
        password = self.reg_password_edit.text()
        if not password:
            self.password_strength_label.setText("Password strength: ")
            self.password_strength_label.setStyleSheet("color: #666; font-size: 10px;")
            return
        
        # Use the password controller to check strength
        strength_info = self.password_controller.check_password_strength(password)
        
        # Update the UI based on strength info
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
        
        self.password_strength_label.setText(f"Password strength: {strength_text}")
        self.password_strength_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
    
    def _on_login_clicked(self):
        """Handle login button click."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username:
            QMessageBox.warning(self, "Validation Error", "Please enter a username.")
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Validation Error", "Please enter a password.")
            self.password_edit.setFocus()
            return
        
        # Emit login signal
        self.login_requested.emit(username, password)
    
    def _on_register_clicked(self):
        """Handle register button click."""
        username = self.reg_username_edit.text().strip()
        password = self.reg_password_edit.text()
        confirm_password = self.reg_confirm_edit.text()
        
        if not username:
            QMessageBox.warning(self, "Validation Error", "Please enter a username.")
            self.reg_username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Validation Error", "Please enter a password.")
            self.reg_password_edit.setFocus()
            return
        
        if not confirm_password:
            QMessageBox.warning(self, "Validation Error", "Please confirm your password.")
            self.reg_confirm_edit.setFocus()
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            self.reg_confirm_edit.setFocus()
            return
        
        # Emit register signal
        self.register_requested.emit(username, password, confirm_password)
    
    def clear_fields(self):
        """Clear all input fields."""
        self.username_edit.clear()
        self.password_edit.clear()
        self.reg_username_edit.clear()
        self.reg_password_edit.clear()
        self.reg_confirm_edit.clear()
        self.password_strength_label.setText("Password strength: ")
        self.password_strength_label.setStyleSheet("color: #666; font-size: 10px;")
    
    def set_login_focus(self):
        """Set focus to login tab."""
        self.tab_widget.setCurrentIndex(0)
        self.username_edit.setFocus()
    
    def set_register_focus(self):
        """Set focus to register tab."""
        self.tab_widget.setCurrentIndex(1)
        self.reg_username_edit.setFocus() 