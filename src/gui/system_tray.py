"""
System tray integration
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QAction


class SystemTray(QObject):
    """System tray icon and menu"""
    
    def __init__(self, main_window, gif_manager):
        super().__init__()
        self.main_window = main_window
        self.gif_manager = gif_manager
        
        self.create_tray_icon()
        self.setup_menu()
        
    def create_tray_icon(self):
        """Create the system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set icon (use a default icon if custom icon not available)
        try:
            icon = QIcon("src/icons/tray_icon.png")
            if icon.isNull():
                # Use default application icon if custom icon not found
                icon = QApplication.style().standardIcon(
                    QApplication.style().StandardPixmap.SP_ComputerIcon
                )
        except:
            icon = QApplication.style().standardIcon(
                QApplication.style().StandardPixmap.SP_ComputerIcon
            )
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Glimmr - Desktop GIF Companion")
        
        # Connect double-click to show/hide main window
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
    def setup_menu(self):
        """Setup the context menu"""
        self.tray_menu = QMenu()
        
        # Show/Hide main window
        self.show_action = QAction("Show Glimmr", self)
        self.show_action.triggered.connect(self.show_main_window)
        self.tray_menu.addAction(self.show_action)
        
        self.hide_action = QAction("Hide Glimmr", self)
        self.hide_action.triggered.connect(self.hide_main_window)
        self.tray_menu.addAction(self.hide_action)
        
        self.tray_menu.addSeparator()
        
        # Companion controls
        self.start_action = QAction("Start Companion", self)
        self.start_action.triggered.connect(self.gif_manager.start)
        self.tray_menu.addAction(self.start_action)
        
        self.stop_action = QAction("Stop Companion", self)
        self.stop_action.triggered.connect(self.gif_manager.stop)
        self.tray_menu.addAction(self.stop_action)
        
        self.tray_menu.addSeparator()
        
        # Test GIF
        self.test_action = QAction("Test Random GIF", self)
        self.test_action.triggered.connect(self.test_gif)
        self.tray_menu.addAction(self.test_action)
        
        self.tray_menu.addSeparator()
        
        # Quit
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit_application)
        self.tray_menu.addAction(self.quit_action)
        
        # Set menu
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Connect to gif manager status updates
        self.gif_manager.status_changed.connect(self.update_menu_state)
        
        # Initial menu state
        self.update_menu_state(self.gif_manager.get_status())
        
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.main_window.isVisible():
                self.hide_main_window()
            else:
                self.show_main_window()
                
    def show_main_window(self):
        """Show the main window"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        
        # Update menu
        self.show_action.setVisible(False)
        self.hide_action.setVisible(True)
        
    def hide_main_window(self):
        """Hide the main window"""
        self.main_window.hide()
        
        # Update menu
        self.show_action.setVisible(True)
        self.hide_action.setVisible(False)
        
    def update_menu_state(self, is_running):
        """Update menu based on companion status"""
        self.start_action.setEnabled(not is_running)
        self.stop_action.setEnabled(is_running)
        
        # Update tooltip
        status = "Running" if is_running else "Stopped"
        self.tray_icon.setToolTip(f"Glimmr - Desktop GIF Companion ({status})")
        
    def test_gif(self):
        """Test display with a random GIF"""
        try:
            self.main_window._test_random_gif()
        except Exception as e:
            print(f"Error testing GIF from tray: {e}")
        
    def show_message(self, title, message, timeout=5000):
        """Show a tray notification"""
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, timeout)
        
    def quit_application(self):
        """Quit the entire application"""
        # Stop the gif manager first
        self.gif_manager.stop()
        
        # Hide tray icon
        self.tray_icon.hide()
        
        # Quit application
        QApplication.quit()
