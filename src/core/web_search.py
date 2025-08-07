"""
Web GIF search and download functionality
"""

import os
import requests
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse


class WebSearchManager:
    """Manages web GIF search and download"""
    
    def __init__(self):
        self.credentials = self._load_credentials()
        self.download_dir = Path(__file__).parent.parent.parent / "downloaded_gifs"
        self.download_dir.mkdir(exist_ok=True)
        
    def _load_credentials(self) -> Dict[str, str]:
        """Load API credentials from environment file"""
        credentials = {}
        
        cred_file = Path(__file__).parent.parent / "credentials.env"
        
        if cred_file.exists():
            try:
                with open(cred_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            credentials[key.strip()] = value.strip()
            except Exception as e:
                print(f"Error loading credentials: {e}")
        
        return credentials
    
    def search_gifs(self, search_term: str, api_source: str = "giphy", limit: int = 40) -> List[Dict[str, Any]]:
        """Search for GIFs using specified API"""
        if api_source.lower() == "giphy":
            return self._search_giphy(search_term, limit)
        elif api_source.lower() == "tenor":
            return self._search_tenor(search_term, limit)
        else:
            raise ValueError(f"Unsupported API source: {api_source}")
    
    def _search_giphy(self, search_term: str, limit: int) -> List[Dict[str, Any]]:
        """Search GIFs using Giphy API"""
        api_key = self.credentials.get('GIPHY_api')
        if not api_key:
            raise Exception("Giphy API key not found in credentials.env")
        
        url = "https://api.giphy.com/v1/gifs/search"
        params = {
            'api_key': api_key,
            'q': search_term,
            'limit': limit,
            'offset': 0,
            'rating': 'g',
            'lang': 'en'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for gif in data.get('data', []):
                result = {
                    'title': gif.get('title', 'Untitled'),
                    'url': gif['images']['original']['url'],
                    'preview_url': gif['images']['preview_gif']['url'],
                    'width': int(gif['images']['original']['width']),
                    'height': int(gif['images']['original']['height']),
                    'size': int(gif['images']['original']['size']),
                    'source': 'giphy',
                    'id': gif['id']
                }
                results.append(result)
            
            return results
            
        except requests.RequestException as e:
            raise Exception(f"Giphy API request failed: {e}")
        except KeyError as e:
            raise Exception(f"Unexpected Giphy API response format: {e}")
    
    def _search_tenor(self, search_term: str, limit: int) -> List[Dict[str, Any]]:
        """Search GIFs using Tenor API"""
        api_key = self.credentials.get('Tenor_api')
        if not api_key:
            raise Exception("Tenor API key not found in credentials.env")
        
        url = "https://tenor.googleapis.com/v2/search"
        params = {
            'key': api_key,
            'q': search_term,
            'limit': limit,
            'media_filter': 'gif',
            'contentfilter': 'medium'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for gif in data.get('results', []):
                # Get the original GIF format
                gif_format = gif['media_formats'].get('gif')
                if not gif_format:
                    continue
                
                result = {
                    'title': gif.get('content_description', 'Untitled'),
                    'url': gif_format['url'],
                    'preview_url': gif['media_formats'].get('tinygif', {}).get('url', gif_format['url']),
                    'width': int(gif_format['dims'][0]),
                    'height': int(gif_format['dims'][1]),
                    'size': int(gif_format.get('size', 0)),
                    'source': 'tenor',
                    'id': gif['id']
                }
                results.append(result)
            
            return results
            
        except requests.RequestException as e:
            raise Exception(f"Tenor API request failed: {e}")
        except KeyError as e:
            raise Exception(f"Unexpected Tenor API response format: {e}")
    
    def download_gif(self, gif_data: Dict[str, Any], custom_download_dir: str = None) -> str:
        """Download a GIF from URL"""
        url = gif_data['url']
        
        # Generate filename
        title = gif_data.get('title', 'untitled')
        title = self._sanitize_filename(title)
        
        # Add source and ID for uniqueness
        source = gif_data.get('source', 'unknown')
        gif_id = gif_data.get('id', 'unknown')
        filename = f"{title}_{source}_{gif_id}.gif"
        
        # Use custom download directory if provided, otherwise use default
        download_dir = Path(custom_download_dir) if custom_download_dir else self.download_dir
        download_dir.mkdir(exist_ok=True)
        
        # Full file path
        file_path = download_dir / filename
        
        # Check if already exists
        if file_path.exists():
            return str(file_path.absolute())
        
        try:
            # Download the file
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save to file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return str(file_path.absolute())
            
        except requests.RequestException as e:
            raise Exception(f"Failed to download GIF: {e}")
        except IOError as e:
            raise Exception(f"Failed to save GIF: {e}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for file system"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        filename = filename[:50]
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure not empty
        if not filename:
            filename = "untitled"
        
        return filename
