"""
Configuration management for Glimmr application
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class AppConfig:
    """Application configuration data class"""
    gif_paths: List[str]
    display_interval: int  # seconds
    # Removed min_display_time
    max_display_time: int  # seconds
    opacity: float  # 0.0 to 1.0
    position: str  # 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    auto_start: bool
    last_window_size: List[int]  # [width, height]
    last_window_position: List[int]  # [x, y]
    gif_size: int = 100  # GIF size in pixels
    custom_positions: Dict[str, Dict[str, int]] = None  # Custom positions for GIFs
    always_on_top: bool = False  # Keep GIFs always on top
    click_through: bool = False  # Allow clicking through GIFs
    download_location: str = ""  # Default download location for search
    position_persistence: bool = True  # Remember GIF positions


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default config path in project root
            self.config_path = Path(__file__).parent.parent.parent / "config.json"
        else:
            self.config_path = Path(config_path)
            
        self.config = self._load_config()
        
    def _get_default_config(self) -> AppConfig:
        """Get default configuration"""
        # Get default GIF paths from Gifs folder
        gifs_folder = Path(__file__).parent.parent.parent / "Gifs"
        default_gifs = []
        
        if gifs_folder.exists():
            # Recursively find all GIF files
            for gif_file in gifs_folder.rglob("*.gif"):
                default_gifs.append(str(gif_file.absolute()))
        
        return AppConfig(
            gif_paths=default_gifs,
            display_interval=1800,  # 30 minutes
            # Removed min_display_time
            max_display_time=10,    # 10 seconds
            opacity=0.9,
            position="center",
            auto_start=False,
            last_window_size=[800, 600],
            last_window_position=[100, 100],
            gif_size=100,           # Default GIF size
            custom_positions={},    # Empty custom positions
            always_on_top=False,    # Default: don't keep on top
            click_through=False,    # Default: don't click through
            download_location=""    # Default: empty, will use Downloads folder
        )
    
    def _load_config(self) -> AppConfig:
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Validate and convert to AppConfig
                default_config = self._get_default_config()
                config_dict = asdict(default_config)
                
                # Update with loaded values
                for key, value in data.items():
                    if key in config_dict:
                        config_dict[key] = value
                
                return AppConfig(**config_dict)
            else:
                # Create default config file
                default_config = self._get_default_config()
                self.save_config(default_config)
                return default_config
                
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def save_config(self, config: AppConfig = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2, ensure_ascii=False)
                
            self.config = config
            
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_config(self) -> AppConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, **kwargs):
        """Update configuration values"""
        config_dict = asdict(self.config)
        config_dict.update(kwargs)
        
        try:
            new_config = AppConfig(**config_dict)
            self.save_config(new_config)
        except Exception as e:
            print(f"Error updating config: {e}")
    
    def add_gif_path(self, path: str):
        """Add a GIF path to the configuration"""
        if path not in self.config.gif_paths:
            self.config.gif_paths.append(path)
            self.save_config()
    
    def remove_gif_path(self, path: str):
        """Remove a GIF path from the configuration"""
        if path in self.config.gif_paths:
            self.config.gif_paths.remove(path)
            self.save_config()
    
    def get_gif_paths(self) -> List[str]:
        """Get list of GIF paths"""
        # Filter out non-existent files
        existing_paths = []
        for path in self.config.gif_paths:
            if os.path.exists(path):
                existing_paths.append(path)
        
        # Update config if some files were removed
        if len(existing_paths) != len(self.config.gif_paths):
            self.config.gif_paths = existing_paths
            self.save_config()
        
        return existing_paths
    
    def update_gif_size(self, size: int):
        """Update GIF size setting"""
        self.config.gif_size = size
        self.save_config()
    
    def update_custom_positions(self, positions: Dict[str, Dict[str, int]]):
        """Update custom positions for GIFs"""
        self.config.custom_positions = positions
        self.save_config()
