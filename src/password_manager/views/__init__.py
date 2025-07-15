"""
Views package for the Password Manager GUI application.
"""

from .main_window import MainWindow
from .auth_widget import AuthWidget
from .dashboard_widget import DashboardWidget
from .entry_dialog import EntryDialog
from .password_generator_dialog import PasswordGeneratorDialog
from .change_password_dialog import ChangePasswordDialog

__all__ = [
    'MainWindow',
    'AuthWidget', 
    'DashboardWidget',
    'EntryDialog',
    'PasswordGeneratorDialog',
    'ChangePasswordDialog'
] 