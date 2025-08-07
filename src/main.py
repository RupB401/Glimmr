#!/usr/bin/env python3
"""
Glimmr - Desktop GIF Companion
Main application entry point
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import MainWindow
from gui.system_tray import SystemTray
from core.config import ConfigManager
from core.gif_manager import GifManager


class GlimmrApp:
    """Main application class"""
    
    def __init__(self):
        # Create QApplication first
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Set application properties
        self.app.setApplicationName("Glimmr")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Glimmr")
        
        try:
            # Initialize components
            self.config_manager = ConfigManager()
            self.gif_manager = GifManager(self.config_manager)
            
            # Create main window
            self.main_window = MainWindow(self.config_manager, self.gif_manager)
            
            # Create system tray (with fallback if not supported)
            try:
                self.system_tray = SystemTray(self.main_window, self.gif_manager)
                self.main_window.set_system_tray(self.system_tray)
            except Exception as tray_error:
                print(f"Warning: System tray not available: {tray_error}")
                self.system_tray = None
            
            # Connect signals
            self.setup_connections()
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            import traceback
            traceback.print_exc()
            # Show error dialog if possible
            try:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(None, "Initialization Error", 
                                   f"Failed to initialize Glimmr:\\n{str(e)}")
            except:
                pass
            raise
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # No need to override closeEvent here - main_window handles it properly
        pass
        
    def run(self):
        """Start the application"""
        # Show main window initially
        self.main_window.show()
        
        # Start the application event loop
        return self.app.exec()


def main():
    """Main function"""
    # Handle command line arguments
    debug_mode = "--debug" in sys.argv
    
    if debug_mode:
        print("Starting Glimmr in debug mode...")
    
    try:
        app = GlimmrApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"Error starting application: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
