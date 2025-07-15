#!/usr/bin/env python3
"""
Main GUI entry point for the Password Manager application.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from password_manager.views.main_window import MainWindow
from password_manager.controllers.main_controller import MainController
from password_manager.password_manager_api import PasswordManagerAPI
from password_manager.config import AppConfig

def setup_logging():
    """Setup logging configuration for the GUI application."""
    log_path = AppConfig.get_log_path()
    
    logging.basicConfig(
        level=getattr(logging, AppConfig.LOG_LEVEL),
        format=AppConfig.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

def create_application():
    """Create and configure the Qt application."""
    app = QApplication(sys.argv)
    app.setApplicationName(AppConfig.APP_NAME)
    app.setApplicationVersion(AppConfig.APP_VERSION)
    app.setOrganizationName(AppConfig.APP_ORGANIZATION)
    
    # Set application style
    app.setStyle('Fusion')
    
    return app

def create_components():
    """Create the main application components with proper dependency injection."""
    # Create the model (API layer) with configured database path
    db_path = str(AppConfig.get_db_path())
    model = PasswordManagerAPI(db_path)
    
    # Create the view (UI layer)
    view = MainWindow()
    
    # Create the controller with dependency injection
    controller = MainController(view=view, model=model)
    
    # Set the controller reference in the view
    view.set_controller(controller)
    
    return view, controller

def main():
    """Main entry point for the GUI application."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")
        
        # Create the Qt application
        app = create_application()
        
        # Create components with proper dependency injection
        main_window, controller = create_components()
        
        # Show the main window
        main_window.show()
        logger.info("Main window displayed successfully")
        
        # Start the event loop
        exit_code = app.exec()
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Fatal error during application startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
