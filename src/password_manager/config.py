"""
Configuration settings for the Password Manager application.
Centralizes all application settings and constants.
"""

from pathlib import Path

class AppConfig:
    """Application configuration settings."""
    
    # Application metadata
    APP_NAME = "Password Manager"
    APP_VERSION = "1.0.0"
    APP_ORGANIZATION = "Password Manager"
    
    # Database settings
    DEFAULT_DB_FILE = "password_manager.db"
    DB_DIRECTORY = Path.cwd()  # Use current working directory instead of home directory
    
    # Logging settings
    LOG_FILE = "password_manager_gui.log"
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File paths
    @classmethod
    def get_db_path(cls) -> Path:
        """Get the database file path."""
        return cls.DB_DIRECTORY / cls.DEFAULT_DB_FILE
    
    @classmethod
    def get_log_path(cls) -> Path:
        """Get the log file path."""
        return cls.DB_DIRECTORY / cls.LOG_FILE
    
    @classmethod
    def get_config_directory(cls) -> Path:
        """Get the configuration directory."""
        return cls.DB_DIRECTORY 