"""
Main application window with working companion functionality
"""

import os
import requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QComboBox, QCheckBox, QGroupBox, QGridLayout, QMessageBox, 
    QLineEdit, QProgressBar, QSplitter, QSlider, QApplication, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QIcon, QPixmap, QMovie

try:
    from ..core.config import ConfigManager
    from ..core.gif_manager import GifManager
    # WebSearchManager will be imported dynamically
except ImportError:
    # Fallback for when running as script
    from core.config import ConfigManager
    from core.gif_manager import GifManager


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self, config_manager: ConfigManager, gif_manager: GifManager):
        super().__init__()
        self.config_manager = config_manager
        self.gif_manager = gif_manager
        self.system_tray = None  # Will be set by main app
        
        # Dynamic import to avoid circular imports
        try:
            from core.web_search import WebSearchManager
            self.web_search = WebSearchManager()
        except ImportError:
            self.web_search = None
        
        self.init_ui()
        self.setup_connections()
        self.load_settings()
        
    def set_system_tray(self, system_tray):
        """Set the system tray reference"""
        self.system_tray = system_tray
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Glimmr - Desktop GIF Companion")
        self.setMinimumSize(350, 200)
        # Set window icon
        icon_path = "E:/python projects/Glimmr/Glimmr App Logo.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create central widget and tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_home_tab()
        self._create_library_tab()
        self._create_search_tab()
        self._create_settings_tab()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
    def _create_home_tab(self):
        """Create the home/control tab with improved UI and functionality"""
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Welcome section
        welcome_group = QGroupBox()
        welcome_group.setTitle("")
        welcome_layout = QVBoxLayout(welcome_group)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(10)

        welcome_text = QLabel("<h2 style='color:#3281c5;'>Welcome to <b>Glimmr</b>!</h2><p>Your desktop GIF companion is ready.<br>Use the tabs above to manage your GIF library, search for new GIFs, and customize your experience.</p>")
        welcome_text.setWordWrap(True)
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_text.setStyleSheet("font-size: 16px; padding: 10px; color: #3281c5;")
        welcome_layout.addWidget(welcome_text)
        layout.addWidget(welcome_group)

        # Status section
        status_group = QGroupBox("Companion Status")
        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(20, 10, 20, 10)
        status_layout.setSpacing(10)

        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 15px; color: red; padding: 6px 12px;")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()
        layout.addWidget(status_group)

        # Control section
        control_group = QGroupBox("Companion Controls")
        control_layout = QHBoxLayout(control_group)
        control_layout.setContentsMargins(20, 10, 20, 10)
        control_layout.setSpacing(20)

        self.start_button = QPushButton("▶ Start Companion")
        self.start_button.setToolTip("Start showing GIF overlays on your desktop.")
        self.start_button.setStyleSheet("font-size: 15px; padding: 10px 24px; background-color: #28a745; color: white; border-radius: 8px;")
        self.start_button.clicked.connect(self.start_companion)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("■ Stop Companion")
        self.stop_button.setToolTip("Stop all GIF overlays.")
        self.stop_button.setStyleSheet("font-size: 15px; padding: 10px 24px; background-color: #dc3545; color: white; border-radius: 8px;")
        self.stop_button.clicked.connect(self.stop_companion)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        test_button = QPushButton("🎲 Test Random GIF")
        test_button.setToolTip("Show a random GIF overlay for 5 seconds to test the functionality.")
        test_button.setStyleSheet("font-size: 15px; padding: 10px 24px; background-color: #007bff; color: white; border-radius: 8px;")
        test_button.clicked.connect(self._test_random_gif)
        control_layout.addWidget(test_button)

        layout.addWidget(control_group)
        layout.addStretch()

        self.tab_widget.addTab(home_widget, "Home")

    def _test_random_gif(self):
        """Show a random GIF overlay for testing from the library"""
        gif_paths = self.config_manager.get_gif_paths()
        import random
        if not gif_paths:
            QMessageBox.information(self, "No GIFs", "Your library is empty! Add GIFs in the Library tab.")
            return
        
        # Test the gif overlay functionality directly
        random_gif = random.choice(gif_paths)
        try:
            # Use gif_manager to show a test GIF
            if hasattr(self.gif_manager, 'show_gif_immediately'):
                self.gif_manager.show_gif_immediately(random_gif)
            else:
                # Fallback: show in a popup preview window
                self._show_test_gif_popup(random_gif)
            
            self.status_bar.showMessage(f"Showing test GIF: {Path(random_gif).name}", 3000)
        except Exception as e:
            print(f"Error showing test GIF: {e}")
            self.status_bar.showMessage(f"Error showing test GIF: {str(e)}", 5000)

    def _show_test_gif_popup(self, gif_path):
        """Show a test GIF in a popup window"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Test GIF - {Path(gif_path).name}")
        dialog.setMinimumSize(400, 400)
        dialog.setModal(False)
        
        layout = QVBoxLayout(dialog)
        
        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gif_label.setStyleSheet("border: 2px solid #28a745; background-color: #2b2b2b; color: #ccc;")
        
        # Create and start the movie
        movie = QMovie(gif_path)
        if movie.isValid():
            movie.setCacheMode(QMovie.CacheMode.CacheAll)
            movie.setScaledSize(movie.frameRect().size().scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
            movie.finished.connect(movie.start)  # Loop
            gif_label.setMovie(movie)
            movie.start()
        else:
            gif_label.setText("Error loading GIF")
        
        layout.addWidget(gif_label)
        
        # Auto-close after 5 seconds
        QTimer.singleShot(5000, dialog.close)
        
        dialog.show()

    def _create_library_tab(self):
        """Create the library tab with simplified but functional design"""
        library_widget = QWidget()
        layout = QVBoxLayout(library_widget)
        
        # Controls
        controls_group = QGroupBox("Library Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        add_files_button = QPushButton("Add GIF Files")
        add_files_button.clicked.connect(self.add_gif_files)
        controls_layout.addWidget(add_files_button)
        
        add_folder_button = QPushButton("Add Folder")
        add_folder_button.clicked.connect(self.add_gif_folder)
        controls_layout.addWidget(add_folder_button)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_gif_list)
        controls_layout.addWidget(refresh_button)
        
        controls_layout.addStretch()
        
        self.gif_count_label = QLabel("Total GIFs: 0")
        controls_layout.addWidget(self.gif_count_label)
        
        layout.addWidget(controls_group)
        
        # Simple GIF list
        self.gif_list = QListWidget()
        self.gif_list.itemClicked.connect(self.on_gif_selected)
        layout.addWidget(self.gif_list)

        # Add preview section (same as search tab, but no preview size slider)
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.library_preview = QLabel("Select a GIF to preview")
        self.library_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.library_preview.setMinimumSize(400, 400)
        self.library_preview.setMaximumSize(600, 600)
        self.library_preview.setStyleSheet("border: 2px solid #555; background-color: #2b2b2b; color: #ccc; font-size: 14px;")
        preview_layout.addWidget(self.library_preview)
        self.library_preview_info = QLabel("No GIF selected")
        self.library_preview_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.library_preview_info.setStyleSheet("color: #666; font-size: 12px;")
        preview_layout.addWidget(self.library_preview_info)
        layout.addWidget(preview_group)
        
        self.tab_widget.addTab(library_widget, "Library")

    def _create_search_tab(self):
        """Create the enhanced search tab with full functionality"""
        search_widget = QWidget()
        main_layout = QVBoxLayout(search_widget)
        
        # Search controls
        search_group = QGroupBox("Online GIF Search")
        search_layout = QVBoxLayout(search_group)
        
        # API selection and search input
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API:"))
        self.api_combo = QComboBox()
        self.api_combo.addItems(["Giphy", "Tenor"])
        api_layout.addWidget(self.api_combo)
        
        api_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search terms (e.g., cat, funny, dance)")
        self.search_input.returnPressed.connect(self.search_gifs)
        api_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_gifs)
        api_layout.addWidget(self.search_button)
        
        search_layout.addLayout(api_layout)
        main_layout.addWidget(search_group)
        
        # Download location
        location_group = QGroupBox("Download Settings")
        location_layout = QHBoxLayout(location_group)
        
        location_layout.addWidget(QLabel("Save to:"))
        self.download_location = QLineEdit()
        self.download_location.setPlaceholderText("Select download folder...")
        location_layout.addWidget(self.download_location)
        
        self.browse_location_button = QPushButton("Browse")
        self.browse_location_button.clicked.connect(self.browse_download_location)
        location_layout.addWidget(self.browse_location_button)
        
        main_layout.addWidget(location_group)
        
        # Results area with enhanced preview
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout(results_group)
        
        # Progress bar
        self.search_progress = QProgressBar()
        self.search_progress.setVisible(False)
        results_layout.addWidget(self.search_progress)
        
        # Create splitter for results and preview
        search_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Results list
        results_list_widget = QWidget()
        results_list_layout = QVBoxLayout(results_list_widget)
        results_list_layout.addWidget(QLabel("Results:"))
        
        self.search_results = QListWidget()
        self.search_results.currentItemChanged.connect(self.update_search_preview)
        results_list_layout.addWidget(self.search_results)
        
        # Download buttons
        download_buttons_layout = QHBoxLayout()
        self.download_button = QPushButton("Download Selected")
        self.download_button.clicked.connect(self.download_selected_gif)
        self.download_button.setEnabled(False)
        download_buttons_layout.addWidget(self.download_button)
        
        self.download_all_button = QPushButton("Download All")
        self.download_all_button.clicked.connect(self.download_all_results)
        download_buttons_layout.addWidget(self.download_all_button)
        
        results_list_layout.addLayout(download_buttons_layout)
        
        # Preview section
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.addWidget(QLabel("Preview:"))
        
        # Search preview
        self.search_preview = QLabel("Select a GIF to preview")
        self.search_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_preview.setMinimumSize(400, 400)
        self.search_preview.setMaximumSize(600, 600)
        self.search_preview.setStyleSheet("border: 2px solid #555; background-color: #2b2b2b; color: #ccc; font-size: 14px;")
        preview_layout.addWidget(self.search_preview)
        
        # Preview size control
        search_size_control_layout = QHBoxLayout()
        search_size_control_layout.addWidget(QLabel("Preview Size:"))
        
        self.search_preview_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.search_preview_size_slider.setRange(200, 800)
        self.search_preview_size_slider.setValue(500)
        self.search_preview_size_slider.valueChanged.connect(lambda: self.update_search_preview_size(self.search_preview_size_slider.value()))
        search_size_control_layout.addWidget(self.search_preview_size_slider)
        
        self.search_preview_size_label = QLabel("500px")
        search_size_control_layout.addWidget(self.search_preview_size_label)
        
        preview_layout.addLayout(search_size_control_layout)
        
        # Preview info
        self.preview_info = QLabel("No GIF selected")
        self.preview_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_info.setStyleSheet("color: #666; font-size: 12px;")
        preview_layout.addWidget(self.preview_info)
        
        preview_widget.setLayout(preview_layout)
        
        # Add to splitter
        search_splitter.addWidget(results_list_widget)
        search_splitter.addWidget(preview_widget)
        search_splitter.setSizes([400, 300])
        results_layout.addWidget(search_splitter)
        main_layout.addWidget(results_group)
        
        self.tab_widget.addTab(search_widget, "Search")

    def _create_settings_tab(self):
        """Create the advanced settings tab with colored sliders and position persistence controls"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # --- Display Settings ---
        display_group = QGroupBox("Display Settings")
        display_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; margin-top: 15px; padding-top: 15px; }")
        display_layout = QGridLayout(display_group)
        
        # Display interval slider
        display_layout.addWidget(QLabel("Display Interval:"), 0, 0)
        
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(1, 1440)  # 1 minute to 24 hours
        self.interval_slider.setValue(5)  # Default 5 minutes
        self.interval_slider.valueChanged.connect(self.update_interval_label)
        display_layout.addWidget(self.interval_slider, 0, 1)
        
        self.interval_label = QLabel("5 minutes")
        display_layout.addWidget(self.interval_label, 0, 2)
        
        display_layout.addWidget(QLabel("Max Display Time:"), 2, 0)
        self.max_time_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_time_slider.setRange(5, 60)
        self.max_time_slider.setValue(10)
        self.max_time_slider.valueChanged.connect(self.update_time_range)
        display_layout.addWidget(self.max_time_slider, 2, 1)
        
        self.time_range_label = QLabel("10 seconds")
        display_layout.addWidget(self.time_range_label, 1, 2, 2, 1)
        
        # GIF size slider
        display_layout.addWidget(QLabel("GIF Size:"), 3, 0)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(100, 800)
        self.size_slider.setValue(200)  # Default 200px
        self.size_slider.valueChanged.connect(self.update_size_label)
        display_layout.addWidget(self.size_slider, 3, 1)
        
        self.size_label = QLabel("200px")
        display_layout.addWidget(self.size_label, 3, 2)
        
        # Opacity slider
        display_layout.addWidget(QLabel("Opacity:"), 4, 0)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(100)  # Default 100%
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        display_layout.addWidget(self.opacity_slider, 4, 1)
        
        self.opacity_label = QLabel("100%")
        display_layout.addWidget(self.opacity_label, 4, 2)
        
        # Position combo
        display_layout.addWidget(QLabel("Position:"), 5, 0)
        self.position_combo = QComboBox()
        self.position_combo.addItems(["random", "top-left", "top-right", "bottom-left", "bottom-right", "center"])
        display_layout.addWidget(self.position_combo, 5, 1)
        
        layout.addWidget(display_group)

        # --- Position Persistence Settings ---
        persistence_group = QGroupBox("Position Memory")
        persistence_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; margin-top: 15px; padding-top: 15px; }")
        persistence_layout = QVBoxLayout(persistence_group)
        persistence_layout.setSpacing(15)

        self.position_persistence_checkbox = QCheckBox("Remember where each GIF was last positioned")
        self.position_persistence_checkbox.setChecked(True)
        self.position_persistence_checkbox.setStyleSheet("font-size: 14px; padding: 5px;")
        persistence_layout.addWidget(self.position_persistence_checkbox)

        # Reset positions button
        reset_positions_btn = QPushButton("Clear All Saved Positions")
        reset_positions_btn.setStyleSheet("font-size: 14px; background: #ffcdd2; color: #b71c1c; border-radius: 8px; padding: 10px 20px; margin-top: 10px;")
        reset_positions_btn.clicked.connect(self.reset_all_positions)
        persistence_layout.addWidget(reset_positions_btn)

        layout.addWidget(persistence_group)

        # --- Behavior Settings ---
        behavior_group = QGroupBox("Behavior Settings")
        behavior_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; margin-top: 15px; padding-top: 15px; }")
        behavior_layout = QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(15)

        self.auto_start_checkbox = QCheckBox("Auto-start companion on launch")
        self.auto_start_checkbox.setStyleSheet("font-size: 14px; padding: 5px;")
        behavior_layout.addWidget(self.auto_start_checkbox)

        self.always_on_top_checkbox = QCheckBox("Always keep GIFs on top")
        self.always_on_top_checkbox.setStyleSheet("font-size: 14px; padding: 5px;")
        behavior_layout.addWidget(self.always_on_top_checkbox)

        self.click_through_checkbox = QCheckBox("Click-through GIFs")
        self.click_through_checkbox.setStyleSheet("font-size: 14px; padding: 5px;")
        behavior_layout.addWidget(self.click_through_checkbox)

        layout.addWidget(behavior_group)

        # --- Save Button ---
        save_button = QPushButton("Save Settings")
        save_button.setStyleSheet("font-size: 16px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976d2, stop:1 #43a047); color: white; border-radius: 10px; padding: 15px 40px; margin-top: 20px;")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        layout.addStretch()

        self.tab_widget.addTab(settings_widget, "Settings")

    def setup_connections(self):
        """Setup signal connections"""
        # Connect GIF manager signals
        self.gif_manager.status_changed.connect(self.update_status)
        
    def update_status(self, is_running):
        """Update the status display"""
        if is_running:
            self.status_label.setText("Status: Running")
            self.status_label.setStyleSheet("font-weight: bold; color: green; font-size: 15px; padding: 6px 12px;")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.status_label.setText("Status: Stopped")
            self.status_label.setStyleSheet("font-weight: bold; color: red; font-size: 15px; padding: 6px 12px;")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def start_companion(self):
        """Start the GIF companion with proper error handling"""
        try:
            gif_count = len(self.config_manager.get_gif_paths())
            if gif_count == 0:
                QMessageBox.warning(
                    self, "No GIFs", 
                    "Please add some GIFs to your collection first!\n\nGo to the Library tab and click 'Add GIF Files' or 'Add Folder' to get started."
                )
                return
            print("Starting GIF companion...")
            self.gif_manager.start()
            self.status_bar.showMessage("Companion started! GIFs will appear on your desktop according to your settings.", 5000)
            # Save running state to config
            self.config_manager.update_config(companion_running=True)
        except Exception as e:
            print(f"Error starting companion: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start companion: {str(e)}")
        
    def stop_companion(self):
        """Stop the GIF companion"""
        try:
            print("Stopping GIF companion...")
            self.gif_manager.stop()
            self.status_bar.showMessage("Companion stopped. All GIF overlays have been closed.", 3000)
            # Save running state to config
            self.config_manager.update_config(companion_running=False)
        except Exception as e:
            print(f"Error stopping companion: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop companion: {str(e)}")

    def add_gif_files(self):
        """Add individual GIF files"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select GIF Files", "", 
            "GIF Files (*.gif);;All Files (*)"
        )
        if file_paths:
            added_count = 0
            for file_path in file_paths:
                if self.gif_manager.add_gif(file_path):
                    added_count += 1
            if added_count > 0:
                self.refresh_gif_list()
                self.status_bar.showMessage(f"Added {added_count} GIF(s)", 3000)
            else:
                QMessageBox.information(self, "No GIFs", "No valid GIF files were added.")

    def add_gif_folder(self):
        """Add entire folder of GIFs"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select GIF Folder", ""
        )
        if folder_path:
            added_count = 0
            for file_path in Path(folder_path).rglob("*.gif"):
                if self.gif_manager.add_gif(str(file_path)):
                    added_count += 1
            if added_count > 0:
                self.refresh_gif_list()
                self.status_bar.showMessage(f"Added {added_count} GIF(s) from folder", 3000)
            else:
                QMessageBox.information(self, "No GIFs", "No GIF files found in selected folder.")

    def refresh_gif_list(self):
        """Refresh the GIF list display"""
        gif_paths = self.config_manager.get_gif_paths()
        self.gif_count_label.setText(f"Total GIFs: {len(gif_paths)}")
        
        self.gif_list.clear()
        for gif_path in gif_paths:
            item = QListWidgetItem(Path(gif_path).name)
            item.setData(Qt.ItemDataRole.UserRole, gif_path)
            self.gif_list.addItem(item)

    def on_gif_selected(self, item):
        """Handle GIF selection from list"""
        gif_path = item.data(Qt.ItemDataRole.UserRole)
        if gif_path and os.path.exists(gif_path):
            # Show preview in the library preview window
            movie = QMovie(gif_path)
            if movie.isValid():
                movie.setCacheMode(QMovie.CacheMode.CacheAll)
                movie.setScaledSize(movie.frameRect().size().scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))
                movie.finished.connect(movie.start)
                self.library_preview.setMovie(movie)
                movie.start()
                self.library_preview.setText("")
                self.library_preview_info.setText(f"{Path(gif_path).name} ({movie.frameRect().width()}x{movie.frameRect().height()})")
            else:
                self.library_preview.setText("Error loading GIF")
                self.library_preview_info.setText("")

    def search_gifs(self):
        """Search for GIFs online with full functionality"""
        search_term = self.search_input.text().strip()
        if not search_term:
            QMessageBox.warning(self, "No Search Term", "Please enter a search term!")
            return
            
        if not self.web_search:
            QMessageBox.warning(self, "Search Unavailable", "Web search functionality is not available.")
            return
        
        self.search_results.clear()
        self.search_preview.setText("Select a GIF to preview")
        self.search_preview.setMovie(None)
        self.search_preview.setPixmap(QPixmap())
        self.download_button.setEnabled(False)
        self.preview_info.setText("No GIF selected")
        
        self.search_progress.setVisible(True)
        self.search_progress.setRange(0, 0)
        self.search_button.setEnabled(False)
        
        # Start search in thread
        api_source = self.api_combo.currentText().lower()
        self.search_thread = SearchThread(search_term, api_source, self.web_search)
        self.search_thread.results_ready.connect(self.on_search_results)
        self.search_thread.error_occurred.connect(self.on_search_error)
        self.search_thread.start()

    def on_search_results(self, results):
        """Handle search results"""
        self.search_progress.setVisible(False)
        self.search_button.setEnabled(True)
        
        if not results:
            self.search_results.addItem("No results found")
            return
        
        for result in results:
            item = QListWidgetItem(f"{result['title']} ({result['width']}x{result['height']})")
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.search_results.addItem(item)
        
        self.status_bar.showMessage(f"Found {len(results)} GIFs", 3000)

    def on_search_error(self, error_msg):
        """Handle search errors"""
        self.search_progress.setVisible(False)
        self.search_button.setEnabled(True)
        QMessageBox.warning(self, "Search Error", f"Search failed: {error_msg}")

    def update_search_preview(self):
        """Update the search preview with animated GIF playback"""
        current_item = self.search_results.currentItem()
        if not current_item:
            self.search_preview.setText("Select a GIF to preview")
            self.search_preview.setMovie(None)
            self.search_preview.setPixmap(QPixmap())
            self._cleanup_search_preview()
            self.download_button.setEnabled(False)
            self.preview_info.setText("No GIF selected")
            return

        self.download_button.setEnabled(True)
        result_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        if not result_data:
            self.search_preview.setText("No data available")
            return

        # Update preview info
        title = result_data.get('title', 'Untitled')
        size_info = f"{result_data.get('width', '?')}x{result_data.get('height', '?')}"
        self.preview_info.setText(f"Title: {title}\nSize: {size_info}")
        
        # Get preview URL - try multiple possible fields
        preview_url = (result_data.get('preview_url') or 
                      result_data.get('url') or 
                      result_data.get('mp4') or
                      result_data.get('webp'))
        
        if not preview_url:
            self.search_preview.setText("No preview URL available")
            return

        try:
            # Cleanup previous preview
            self._cleanup_search_preview()
            
            # Show loading
            self.search_preview.setText("🔄 Loading GIF preview...")
            self.search_preview.setStyleSheet("border: 2px solid #007bff; background-color: #f8f9fa; color: #007bff; font-weight: bold;")
            
            # Force GUI update
            QApplication.processEvents()
            
            # Download GIF data with proper headers
            response = requests.get(preview_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            # Create movie from data
            self._gif_data_ref = QByteArray(response.content)
            self.search_preview_buffer = QBuffer(self._gif_data_ref)
            self.search_preview_buffer.open(QIODevice.OpenModeFlag.ReadOnly)

            self.search_preview_movie = QMovie()
            self.search_preview_movie.setDevice(self.search_preview_buffer)

            if self.search_preview_movie.isValid():
                self.search_preview_movie.setCacheMode(QMovie.CacheMode.CacheAll)
                self.search_preview_movie.setSpeed(100)
                
                # Set up looping
                self.search_preview_movie.finished.connect(self.search_preview_movie.start)

                # Scale movie
                preview_size = self.search_preview_size_slider.value()
                original_size = self.search_preview_movie.frameRect().size()
                if not original_size.isEmpty():
                    scaled_size = original_size.scaled(preview_size, preview_size, Qt.AspectRatioMode.KeepAspectRatio)
                    self.search_preview_movie.setScaledSize(scaled_size)

                # Start preview
                self.search_preview.setMovie(self.search_preview_movie)
                self.search_preview_movie.start()
                self.search_preview.setText("")
                self.search_preview.setStyleSheet("border: 2px solid #28a745; background-color: #2b2b2b; color: #ccc;")
            else:
                # Fallback to static image
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                if not pixmap.isNull():
                    preview_size = self.search_preview_size_slider.value()
                    scaled_pixmap = pixmap.scaled(
                        preview_size, preview_size, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.search_preview.setPixmap(scaled_pixmap)
                    self.search_preview.setText("")
                    self.search_preview.setStyleSheet("border: 2px solid #ffc107; background-color: #2b2b2b; color: #ccc;")
                else:
                    raise Exception("Invalid image format")

        except Exception as e:
            print(f"Preview error: {e}")
            self.search_preview.setText("❌ Preview failed to load")
            self.search_preview.setMovie(None)
            self.search_preview.setStyleSheet("border: 2px solid #dc3545; background-color: #2b2b2b; color: #dc3545; font-weight: bold;")

    def _cleanup_search_preview(self):
        """Helper method to cleanup search preview resources"""
        if hasattr(self, 'search_preview_movie') and self.search_preview_movie:
            try:
                self.search_preview_movie.stop()
                self.search_preview_movie.setDevice(None)
                self.search_preview_movie = None
            except:
                pass
        
        if hasattr(self, 'search_preview_buffer') and self.search_preview_buffer:
            try:
                self.search_preview_buffer.close()
                self.search_preview_buffer = None
            except:
                pass

    def update_search_preview_size(self, size):
        """Update search preview size and refresh if movie is playing"""
        self.search_preview.setMinimumSize(size, size)
        self.search_preview.setMaximumSize(size + 200, size + 200)  # Allow extra room for animation
        self.search_preview_size_label.setText(f"{size}px")
        
        # Update current preview if available
        if hasattr(self, 'search_preview_movie') and self.search_preview_movie:
            try:
                # Resize current movie
                original_size = self.search_preview_movie.frameRect().size()
                if not original_size.isEmpty():
                    scaled_size = original_size.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio)
                    self.search_preview_movie.setScaledSize(scaled_size)
            except Exception as e:
                print(f"Error updating preview size: {e}")

    def browse_download_location(self):
        """Browse for download location"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Download Folder", 
            self.download_location.text() or str(Path.home() / "Downloads")
        )
        if folder_path:
            self.download_location.setText(folder_path)

    def download_selected_gif(self):
        """Download selected GIF from search results"""
        current_item = self.search_results.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a GIF to download!")
            return
        
        # Check if download location is set, use default if not
        download_path = self.download_location.text().strip()
        if not download_path:
            # Use user-specified default path
            default_path = "E:/python projects/Glimmr/Gifs"
            if os.path.exists(default_path):
                download_path = default_path
                print(f"Using default download location: {download_path}")
            else:
                QMessageBox.warning(self, "No Download Location", 
                                  f"Default download location does not exist: {default_path}\nPlease select a download location first!")
                return
        
        if not os.path.exists(download_path):
            QMessageBox.warning(self, "Invalid Location", 
                              f"Selected download location does not exist: {download_path}")
            return

        # Save last used download location to config
        try:
            self.config_manager.update_config(download_location=download_path)
        except Exception as e:
            print(f"Error saving last download location: {e}")
        
        result_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        try:
            # Show progress
            self.search_progress.setVisible(True)
            self.search_progress.setRange(0, 0)
            
            # Start download in thread
            self.download_thread = DownloadThread(result_data, self.web_search, download_path)
            self.download_thread.download_finished.connect(self.on_download_finished)
            self.download_thread.download_error.connect(self.on_download_error)
            self.download_thread.start()
            
        except Exception as e:
            self.search_progress.setVisible(False)
            QMessageBox.critical(self, "Download Error", f"Failed to start download: {str(e)}")

    def download_all_results(self):
        """Download all search results"""
        if self.search_results.count() == 0:
            QMessageBox.information(self, "No Results", "No search results to download.")
            return
        
        reply = QMessageBox.question(
            self, "Download All",
            f"Download all {self.search_results.count()} GIFs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Feature Coming Soon", 
                                  "Bulk download feature will be implemented in a future update.\nFor now, please download GIFs individually.")

    def on_download_finished(self, file_path):
        """Handle successful download"""
        self.search_progress.setVisible(False)
        self.status_bar.showMessage(f"Downloaded: {Path(file_path).name}", 5000)
        
        # Automatically add downloaded GIF to library
        try:
            print(f"Adding downloaded GIF to library: {file_path}")
            self.config_manager.add_gif_path(file_path)
            print(f"Successfully added {file_path} to config")
            self.refresh_gif_list()  # Refresh the library view
            success_msg = f"GIF saved to:\n{file_path}\n\nAutomatically added to your library!"
        except Exception as e:
            print(f"Error adding GIF to library: {e}")
            import traceback
            traceback.print_exc()
            success_msg = f"GIF saved to:\n{file_path}\n\nNote: Could not automatically add to library."
        
        QMessageBox.information(self, "Download Complete", success_msg)

    def on_download_error(self, error_msg):
        """Handle download error"""
        self.search_progress.setVisible(False)
        QMessageBox.critical(self, "Download Error", f"Download failed: {error_msg}")

    def save_settings(self):
        """Save current settings"""
        try:
            self.config_manager.update_config(
                display_interval=self.interval_slider.value() * 60,  # Convert minutes to seconds
                max_display_time=self.max_time_slider.value(),
                gif_size=self.size_slider.value(),
                opacity=self.opacity_slider.value() / 100.0,
                position=self.position_combo.currentText(),
                auto_start=self.auto_start_checkbox.isChecked(),
                always_on_top=self.always_on_top_checkbox.isChecked(),
                click_through=self.click_through_checkbox.isChecked(),
                position_persistence=self.position_persistence_checkbox.isChecked(),
                download_location=self.download_location.text()
            )
            self.status_bar.showMessage("Settings saved successfully", 3000)
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")
            import traceback
            traceback.print_exc()

    def reset_all_positions(self):
        """Reset all saved GIF positions"""
        try:
            self.config_manager.update_custom_positions({})
            QMessageBox.information(self, "Positions Reset", "All saved GIF positions have been reset.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to reset positions: {e}")

    # Settings-related methods
    def update_interval_label(self, value):
        """Update interval label when slider changes"""
        if value < 60:
            self.interval_label.setText(f"{value} minutes")
        else:
            hours = value // 60
            minutes = value % 60
            if minutes == 0:
                self.interval_label.setText(f"{hours} hour{'s' if hours > 1 else ''}")
            else:
                self.interval_label.setText(f"{hours}h {minutes}m")
    
    def update_time_range(self):
        """Update time range label when slider changes"""
        max_val = self.max_time_slider.value()
        self.time_range_label.setText(f"{max_val} seconds")
    
    def update_size_label(self, value):
        """Update size label when slider changes"""
        self.size_label.setText(f"{value}px")
        
        # Update config immediately for real-time effect
        try:
            self.config_manager.update_config(gif_size=value)
        except Exception as e:
            print(f"Error updating gif size in config: {e}")
        
        # Apply size change to any current overlays
        if hasattr(self, 'gif_manager'):
            self.gif_manager.apply_size_to_overlays(value)
    
    def update_opacity_label(self, value):
        """Update opacity label when slider changes"""
        self.opacity_label.setText(f"{value}%")

    def load_settings(self):
        """Load settings from configuration"""
        try:
            config = self.config_manager.get_config()
            
            # Load display settings to sliders with defaults matching the UI
            self.interval_slider.setValue(getattr(config, 'display_interval', 300) // 60)  # Default 5 minutes
            self.max_time_slider.setValue(getattr(config, 'max_display_time', 10))  # Default 10 seconds
            self.size_slider.setValue(getattr(config, 'gif_size', 200))  # Default 200px 
            self.opacity_slider.setValue(int(getattr(config, 'opacity', 1.0) * 100))  # Default 100%
            self.position_combo.setCurrentText(getattr(config, 'position', 'random'))  # Default random
            
            # Load checkboxes with defaults
            self.auto_start_checkbox.setChecked(getattr(config, 'auto_start', True))  # Default True
            self.always_on_top_checkbox.setChecked(getattr(config, 'always_on_top', True))  # Default True
            self.click_through_checkbox.setChecked(getattr(config, 'click_through', False))  # Default False
            
            # Load position persistence
            self.position_persistence_checkbox.setChecked(getattr(config, 'position_persistence', True))
            
            # Load download location
            download_location = getattr(config, 'download_location', "E:/python projects/Glimmr/Gifs")
            self.download_location.setText(download_location)
            
            # Update labels
            self.update_interval_label(self.interval_slider.value())
            self.update_time_range()
            self.update_size_label(self.size_slider.value())
            self.update_opacity_label(self.opacity_slider.value())
            
            # Load window settings
            if hasattr(config, 'last_window_size') and config.last_window_size:
                self.resize(*config.last_window_size)
            if hasattr(config, 'last_window_position') and config.last_window_position:
                self.move(*config.last_window_position)
                
            # Refresh the library
            self.refresh_gif_list()
            
            # Load companion running state and update buttons
            companion_running = getattr(config, 'companion_running', False)
            if companion_running:
                self.gif_manager.start()
                self.update_status(True)
            else:
                self.update_status(False)
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            import traceback
            traceback.print_exc()

    def closeEvent(self, event):
        """Handle window close event - minimize to tray instead of closing"""
        # Save window position and size
        try:
            self.config_manager.update_config(
                last_window_size=[self.width(), self.height()],
                last_window_position=[self.x(), self.y()]
            )
        except Exception as e:
            print(f"Error saving window settings: {e}")
        
        # Don't actually close the app, just hide the window
        event.ignore()
        self.hide()
        
        # Show system tray message if available
        try:
            if self.system_tray:
                self.system_tray.show_message(
                    "Glimmr", 
                    "Application was minimized to tray. GIF companion will continue running.",
                    2000
                )
        except Exception as e:
            print(f"Error showing tray message: {e}")
        
        # Show status message
        self.status_bar.showMessage("Application minimized to system tray", 3000)
        
    def quit_application(self):
        """Actually quit the application"""
        # Stop companion if running
        if self.gif_manager.get_status():
            self.gif_manager.stop()
        
        # Quit the application
        QApplication.quit()


class SearchThread(QThread):
    """Thread for searching GIFs"""
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, search_term, api_source, web_search):
        super().__init__()
        self.search_term = search_term
        self.api_source = api_source
        self.web_search = web_search
        self.finished.connect(self.cleanup)  # Ensure cleanup when thread finishes
        
    def cleanup(self):
        """Cleanup thread resources"""
        try:
            self.quit()
        except:
            pass
        
    def run(self):
        try:
            results = self.web_search.search_gifs(self.search_term, self.api_source)
            self.results_ready.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DownloadThread(QThread):
    """Thread for downloading GIFs"""
    download_finished = pyqtSignal(str)
    download_error = pyqtSignal(str)
    
    def __init__(self, result_data, web_search, download_path=None):
        super().__init__()
        self.result_data = result_data
        self.web_search = web_search
        self.download_path = download_path
        self.finished.connect(self.cleanup)  # Ensure cleanup when thread finishes
        
    def cleanup(self):
        """Cleanup thread resources"""
        try:
            self.quit()
        except:
            pass
        
    def run(self):
        try:
            # Download logic goes here
            if hasattr(self, 'download_path') and self.download_path:
                file_path = self.web_search.download_gif(self.result_data, self.download_path)
            else:
                file_path = self.web_search.download_gif(self.result_data)
            # Emit success signal
            self.download_finished.emit(file_path)
        except Exception as e:
            # Emit error signal
            self.download_error.emit(str(e))
