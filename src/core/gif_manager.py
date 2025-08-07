"""
GIF management and display logic
"""

import random
import os
from pathlib import Path
from typing import List, Optional
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from .config import ConfigManager
# Import will be done dynamically to avoid circular imports


class GifManager(QObject):
    """Manages GIF display logic and timing"""
    
    # Signals
    gif_displayed = pyqtSignal(str)  # Emitted when a GIF is displayed
    gif_hidden = pyqtSignal()        # Emitted when a GIF is hidden
    status_changed = pyqtSignal(bool)  # Emitted when running status changes
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.is_running = False
        
        # Timers
        self.display_timer = QTimer()
        self.hide_timer = QTimer()
        
        # GIF overlay
        self.gif_overlay = None
        
        # Setup timers
        self.display_timer.setSingleShot(True)
        self.hide_timer.setSingleShot(True)
        
        self.display_timer.timeout.connect(self._show_random_gif)
        self.hide_timer.timeout.connect(self._hide_gif)
        
    def start(self):
        """Start the GIF display cycle"""
        if not self.is_running:
            self.is_running = True
            self.status_changed.emit(True)
            self._schedule_next_display()
            print("GIF Manager started")
    
    def stop(self):
        """Stop the GIF display cycle"""
        if self.is_running:
            self.is_running = False
            self.status_changed.emit(False)
            self.display_timer.stop()
            self.hide_timer.stop()
            self._hide_gif()
            print("GIF Manager stopped")
    
    def _schedule_next_display(self):
        """Schedule the next GIF display"""
        if not self.is_running:
            print("Not scheduling next display - manager is stopped")
            return
            
        config = self.config_manager.get_config()
        interval_ms = config.display_interval * 1000
        
        self.display_timer.start(interval_ms)
        print(f"Next GIF scheduled in {config.display_interval} seconds")
    
    def _show_random_gif(self):
        """Display a random GIF"""
        if not self.is_running:
            return
            
        gif_paths = self.config_manager.get_gif_paths()
        
        if not gif_paths:
            print("No GIFs available to display")
            self._schedule_next_display()
            return
        
        # Select random GIF
        selected_gif = random.choice(gif_paths)
        
        # Verify file exists
        if not os.path.exists(selected_gif):
            print(f"GIF file not found: {selected_gif}")
            self.config_manager.remove_gif_path(selected_gif)
            self._schedule_next_display()
            return
        
        # Create and show overlay
        self._create_overlay(selected_gif)
        
        # Schedule hiding - use max_display_time only
        config = self.config_manager.get_config()
        display_duration = config.max_display_time
        
        self.hide_timer.start(display_duration * 1000)
        
        # Emit signal
        self.gif_displayed.emit(selected_gif)
        print(f"Displaying: {Path(selected_gif).name} for {display_duration}s")
    
    def _create_overlay(self, gif_path: str):
        """Create and show the GIF overlay"""
        # Hide existing overlay if any
        self._hide_gif()
        
        config = self.config_manager.get_config()
        
        # Dynamic import to avoid circular imports
        from gui.gif_overlay import GifOverlay
        
        try:
            # Create new overlay - pass config_manager for position persistence
            self.gif_overlay = GifOverlay(gif_path, config, self.config_manager)
            
            # Keep a strong reference to prevent garbage collection
            self.gif_overlay.setParent(None)  # Ensure it's not accidentally parented
            
            self.gif_overlay.show()
            print(f"Created and showed GIF overlay for: {gif_path}")
        except Exception as e:
            print(f"Error creating GIF overlay: {e}")
            self.gif_overlay = None
    
    def _hide_gif(self):
        """Hide the current GIF"""
        if self.gif_overlay:
            try:
                if not self.gif_overlay.isVisible():
                    # Already closed/hidden, just clean up reference
                    self.gif_overlay = None
                else:
                    self.gif_overlay.close()
                    self.gif_overlay = None
                self.gif_hidden.emit()
            except RuntimeError as e:
                # Object already deleted by Qt, just clean up reference
                print(f"GIF overlay already deleted: {e}")
                self.gif_overlay = None
                self.gif_hidden.emit()
            except Exception as e:
                print(f"Error hiding GIF: {e}")
                self.gif_overlay = None
        
        # Schedule next display if still running
        if self.is_running:
            print("Scheduling next GIF display after hiding current one")
            self._schedule_next_display()
        else:
            print("Not scheduling next display - manager stopped")
    
    def get_status(self) -> bool:
        """Get current running status"""
        return self.is_running
    
    def get_available_gifs(self) -> List[str]:
        """Get list of available GIF files"""
        return self.config_manager.get_gif_paths()
    
    def add_gif(self, gif_path: str) -> bool:
        """Add a new GIF to the collection"""
        if not os.path.exists(gif_path):
            return False
        
        if not gif_path.lower().endswith('.gif'):
            return False
        
        self.config_manager.add_gif_path(gif_path)
        return True
    
    def remove_gif(self, gif_path: str) -> bool:
        """Remove a GIF from the collection"""
        try:
            self.config_manager.remove_gif_path(gif_path)
            return True
        except Exception as e:
            print(f"Error removing GIF: {e}")
            return False
    
    def show_gif_immediately(self, gif_path: str):
        """Show a specific GIF immediately (for preview)"""
        if os.path.exists(gif_path):
            self._create_overlay(gif_path)
            
            # Auto-hide after 5 seconds
            QTimer.singleShot(5000, self._hide_gif)
    
    def apply_size_to_overlays(self, size):
        """Apply size change to any currently displayed overlays"""
        try:
            if self.gif_overlay and hasattr(self.gif_overlay, 'set_gif_size'):
                self.gif_overlay.set_gif_size(size)
                print(f"Applied size {size}px to current overlay")
        except Exception as e:
            print(f"Error applying size to overlays: {e}")
