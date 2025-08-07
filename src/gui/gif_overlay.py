"""
Enhanced GIF overlay window with drag & drop positioning and size control
"""

import os
import json
import random
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint
from PyQt6.QtGui import QMovie, QScreen, QCursor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from ..core.config import AppConfig
    except ImportError:
        from core.config import AppConfig
else:
    try:
        from ..core.config import AppConfig
    except ImportError:
        from core.config import AppConfig


class GifOverlay(QWidget):
    """Enhanced transparent overlay window for displaying draggable GIFs"""
    
    def __init__(self, gif_path: str, config: 'AppConfig', config_manager=None):
        super().__init__()
        self.gif_path = gif_path
        self.config = config
        self.config_manager = config_manager
        self.dragging = False
        self.drag_start_position = QPoint()
        
        self.init_ui()
        self.setup_window()
        self.load_gif()
        
    def init_ui(self):
        """Initialize the UI components"""
        # Set window flags for overlay with enhanced interaction
        flags = (
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        
        # Only add click-through if explicitly enabled and position persistence is disabled
        click_through = getattr(self.config, 'click_through', False)
        position_persistence = getattr(self.config, 'position_persistence', True)
        
        # Don't use click-through if position persistence is enabled (for dragging)
        if click_through and not position_persistence:
            flags |= Qt.WindowType.WindowTransparentForInput
        
        self.setWindowFlags(flags)
        
        # Set transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create GIF label with enhanced styling
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setStyleSheet("""
            QLabel {
                border: 2px solid transparent;
                border-radius: 8px;
            }
            QLabel:hover {
                border: 2px solid rgba(100, 149, 237, 0.8);
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout.addWidget(self.gif_label)
        
    def setup_window(self):
        """Setup window properties with enhanced positioning"""
        # Set initial opacity
        opacity = self.config.opacity if hasattr(self.config, 'opacity') else 0.9
        self.setWindowOpacity(opacity)
        
        # Load custom position if it exists
        custom_positions = getattr(self.config, 'custom_positions', {})
        gif_name = Path(self.gif_path).name
        
        if gif_name in custom_positions:
            # Use saved custom position
            pos = custom_positions[gif_name]
            self.move(pos['x'], pos['y'])
            if 'width' in pos and 'height' in pos:
                self.resize(pos['width'], pos['height'])
        else:
            # Use default positioning
            self._position_window_default()
            
    def _position_window_default(self):
        """Position the window based on configuration"""
        # Get primary screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Default size (will be adjusted when GIF loads) - increased for larger GIFs
        default_size = getattr(self.config, 'gif_size', 400)
        window_size = QRect(0, 0, default_size, default_size)
        
        position = self.config.position.lower()
        
        if position == "random":
            # Random position with some padding from screen edges
            padding = 100
            max_x = screen_geometry.width() - window_size.width() - padding
            max_y = screen_geometry.height() - window_size.height() - padding
            x = random.randint(padding, max_x) if max_x > padding else padding
            y = random.randint(padding, max_y) if max_y > padding else padding
        elif position == "center":
            x = (screen_geometry.width() - window_size.width()) // 2
            y = (screen_geometry.height() - window_size.height()) // 2
        elif position == "top-left":
            x = 50
            y = 50
        elif position == "top-right":
            x = screen_geometry.width() - window_size.width() - 50
            y = 50
        elif position == "bottom-left":
            x = 50
            y = screen_geometry.height() - window_size.height() - 50
        elif position == "bottom-right":
            x = screen_geometry.width() - window_size.width() - 50
            y = screen_geometry.height() - window_size.height() - 50
        else:
            # Default to center
            x = (screen_geometry.width() - window_size.width()) // 2
            y = (screen_geometry.height() - window_size.height()) // 2
        
        self.move(x, y)
        
    def load_gif(self):
        """Load and display the GIF with size control"""
        if not os.path.exists(self.gif_path):
            print(f"GIF file not found: {self.gif_path}")
            self.close()
            return
        
        try:
            # Create QMovie for animated GIF
            self.movie = QMovie(self.gif_path)
            
            if not self.movie.isValid():
                print(f"Invalid GIF file: {self.gif_path}")
                self.close()
                return
            
            # Set the movie to the label
            self.gif_label.setMovie(self.movie)
            
            # Apply current size setting
            self.apply_size_setting()
            
            # Connect to first frame to adjust window size
            self.movie.frameChanged.connect(self._adjust_window_size)
            
            # Set up display duration if configured
            self.setup_display_duration()
            
            # Start the animation
            self.movie.start()
            
        except Exception as e:
            print(f"Error loading GIF: {e}")
    
    def apply_size_setting(self):
        """Apply current size setting to the GIF"""
        try:
            # Get size from config or use default
            gif_size = getattr(self.config, 'gif_size', 400)  # Default to 400px
            
            # Set scaled size for the movie
            if hasattr(self.movie, 'scaledSize'):
                from PyQt6.QtCore import QSize
                self.movie.setScaledSize(QSize(gif_size, gif_size))
            
        except Exception as e:
            print(f"Error applying size setting: {e}")
    
    def set_gif_size(self, size):
        """Dynamically change GIF size"""
        try:
            from PyQt6.QtCore import QSize
            if hasattr(self, 'movie') and self.movie:
                self.movie.setScaledSize(QSize(size, size))
                
                # Adjust window size and save position
                self.save_custom_position(include_size=True)
        except Exception as e:
            print(f"Error setting GIF size: {e}")
            self.close()
    
    def _adjust_window_size(self):
        """Adjust window size to match GIF dimensions"""
        if hasattr(self, '_size_adjusted'):
            return
        
        self._size_adjusted = True
        
        # Get GIF size
        gif_size = self.movie.currentPixmap().size()
        
        # Apply size multiplier from config
        target_size = getattr(self.config, 'gif_size', 400)  # Default to 400px
        
        # Calculate scale factor to achieve target size
        # Use the larger dimension as reference
        larger_dimension = max(gif_size.width(), gif_size.height())
        scale_factor = target_size / larger_dimension if larger_dimension > 0 else 1
        
        width = int(gif_size.width() * scale_factor)
        height = int(gif_size.height() * scale_factor)
        
        # Apply minimum and maximum limits
        min_size = 100
        max_size = 800
        
        # Ensure minimum size
        if width < min_size or height < min_size:
            scale_up = min_size / min(width, height)
            width = int(width * scale_up)
            height = int(height * scale_up)
        
        # Limit maximum size while preserving aspect ratio
        if width > max_size or height > max_size:
            aspect_ratio = width / height
            if width > height:
                width = max_size
                height = int(max_size / aspect_ratio)
            else:
                height = max_size
                width = int(max_size * aspect_ratio)
        
        self.resize(width, height)
        
        # Disconnect the signal to avoid multiple calls
        self.movie.frameChanged.disconnect(self._adjust_window_size)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging and interaction"""
        click_through = getattr(self.config, 'click_through', False)
        position_persistence = getattr(self.config, 'position_persistence', True)
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Only allow dragging if not in click-through mode or if position persistence is enabled
            if not click_through or position_persistence:
                # Start dragging
                self.dragging = True
                self.drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                event.accept()
                print(f"Started dragging from position: {event.globalPosition().toPoint()}")
            
        elif event.button() == Qt.MouseButton.RightButton:
            # Right click to close (if not click-through)
            if not click_through:
                self.close()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            # Calculate new position
            new_pos = event.globalPosition().toPoint() - self.drag_start_position
            self.move(new_pos)
            event.accept()
            print(f"Dragging to position: {new_pos}")
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to end dragging and save position"""
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            
            # Save the new position
            self.save_custom_position()
            event.accept()
        
        super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        """Show resize cursor on hover"""
        click_through = getattr(self.config, 'click_through', False)
        position_persistence = getattr(self.config, 'position_persistence', True)
        
        # Only show drag cursor if dragging is allowed
        if not click_through or position_persistence:
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Reset cursor when leaving"""
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().leaveEvent(event)
    
    def save_custom_position(self, include_size=False):
        """Save the current position as a custom position for this GIF"""
        try:
            # Check if position persistence is enabled
            if not getattr(self.config, 'position_persistence', True):
                return
                
            # Get current position and size
            pos = self.pos()
            size = self.size()
            gif_name = Path(self.gif_path).name
            
            # Load existing custom positions
            custom_positions = getattr(self.config, 'custom_positions', {})
            
            # Save position and optionally size
            position_data = {
                'x': pos.x(),
                'y': pos.y()
            }
            
            if include_size:
                position_data.update({
                    'width': size.width(),
                    'height': size.height()
                })
            
            custom_positions[gif_name] = position_data
            
            # Update config using config_manager
            if self.config_manager and hasattr(self.config_manager, 'update_custom_positions'):
                self.config_manager.update_custom_positions(custom_positions)
                print(f"Saved custom position for {gif_name}: {pos.x()}, {pos.y()}")
            else:
                print("Config manager not available for saving position")
            
        except Exception as e:
            print(f"Error saving custom position: {e}")
    
    def setup_display_duration(self):
        """Setup display duration timer if configured"""
        try:
            # Get maximum duration from config
            max_duration = getattr(self.config, 'max_display_time', 30)

            # Use maximum duration only
            duration = max_duration * 1000  # Convert to milliseconds

            # Set up timer to close the overlay
            self.display_timer = QTimer()
            self.display_timer.timeout.connect(self.close)
            self.display_timer.setSingleShot(True)
            self.display_timer.start(duration)

        except Exception as e:
            print(f"Error setting up display duration: {e}")
    
    def wheelEvent(self, event):
        """Handle mouse wheel for resizing"""
        if not getattr(self.config, 'click_through', False):
            # Get wheel delta
            delta = event.angleDelta().y()
            
            # Calculate size change (±10%)
            current_size = self.size()
            scale_factor = 1.1 if delta > 0 else 0.9
            
            new_width = int(current_size.width() * scale_factor)
            new_height = int(current_size.height() * scale_factor)
            
            # Apply limits
            min_size = 50
            max_size = 800
            
            new_width = max(min_size, min(max_size, new_width))
            new_height = max(min_size, min(max_size, new_height))
            
            # Resize the window
            self.resize(new_width, new_height)
            
            # Save the new size
            self.save_custom_position()
            
            event.accept()
        
        super().wheelEvent(event)
    
    def closeEvent(self, event):
        """Clean up when closing"""
        if hasattr(self, 'movie'):
            self.movie.stop()
        super().closeEvent(event)
