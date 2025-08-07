#!/usr/bin/env python3
"""
Convert PNG icon to ICO format for PyInstaller
"""

from PIL import Image
import os

def convert_png_to_ico(png_path, ico_path):
    """Convert PNG to ICO format"""
    try:
        # Open the PNG image
        img = Image.open(png_path)
        
        # Create multiple sizes for better compatibility
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Resize and save as ICO with multiple sizes
        img.save(ico_path, format='ICO', sizes=sizes)
        print(f"✅ Successfully converted {png_path} to {ico_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error converting icon: {e}")
        return False

if __name__ == "__main__":
    png_path = "E:/python projects/Glimmr/Glimmr App Logo.png"
    ico_path = "E:/python projects/Glimmr/Glimmr_App_Logo.ico"
    
    if os.path.exists(png_path):
        convert_png_to_ico(png_path, ico_path)
    else:
        print(f"❌ PNG file not found: {png_path}")
