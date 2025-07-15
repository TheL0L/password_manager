"""
Error handling utilities for the Password Manager.
Provides centralized error handling and formatting.
"""

import logging

class ErrorHandler:
    """Centralized error handling for the application."""
    
    @staticmethod
    def handle_api_error(operation: str, error: Exception, logger: logging.Logger) -> str:
        """Handle API-related errors consistently."""
        error_msg = f"{operation} error: {str(error)}"
        logger.error(f"{operation} exception: {error}")
        return error_msg
    
    @staticmethod
    def handle_validation_error(field: str, message: str) -> str:
        """Handle validation errors consistently."""
        return f"Validation error - {field}: {message}"
    
    @staticmethod
    def handle_authentication_error(message: str) -> str:
        """Handle authentication errors consistently."""
        return f"Authentication error: {message}"
    
    @staticmethod
    def handle_database_error(operation: str, error: Exception, logger: logging.Logger) -> str:
        """Handle database-related errors."""
        error_msg = f"Database {operation} error: {str(error)}"
        logger.error(f"Database {operation} exception: {error}")
        return error_msg
    
    @staticmethod
    def handle_encryption_error(operation: str, error: Exception, logger: logging.Logger) -> str:
        """Handle encryption-related errors."""
        error_msg = f"Encryption {operation} error: {str(error)}"
        logger.error(f"Encryption {operation} exception: {error}")
        return error_msg
    
    @staticmethod
    def format_error_message(error_type: str, details: str, context: str = "") -> str:
        """Format error messages consistently."""
        if context:
            return f"{error_type}: {details} (Context: {context})"
        return f"{error_type}: {details}"
    
    @staticmethod
    def log_and_format_error(error: Exception, operation: str, logger: logging.Logger) -> tuple[str, str]:
        """Log error and return formatted error message."""
        error_msg = f"{operation} failed: {str(error)}"
        logger.error(f"{operation} exception: {error}")
        return error_msg, str(error) 