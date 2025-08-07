# Glimmr - Desktop GIF Companion

A PyQt6 desktop application that displays animated GIFs as desktop companions, overlaying them on top of active windows at random intervals.

## Features

- 🎭 **Desktop Companion**: GIFs appear over your active window at customizable intervals
- 🎲 **Random Display**: Each GIF shows for a random duration within your set range
- 📁 **Local GIF Management**: Add, remove, and organize your own GIF collection
- 🌐 **Web GIF Search**: Browse and download GIFs from Giphy and Tenor APIs
- ⚙️ **Customizable Settings**: Adjust intervals, display duration, opacity, and position
- 🎯 **System Tray**: Minimalistic interface with system tray integration
- 🎨 **Clean UI**: Simple and sober design with tabbed interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Glimmr
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API credentials:
   - Copy your Giphy and Tenor API keys to `src/credentials.env`
   - Get free API keys from:
     - [Giphy Developers](https://developers.giphy.com/)
     - [Tenor API](https://tenor.com/gifapi)

4. Run the application:
```bash
python src/main.py
```

## Usage

### Getting Started
1. Launch the application
2. Use the **Home** tab to start/stop the companion
3. Manage your GIF collection in the **GIF Library** tab
4. Search and download new GIFs in the **Search** tab
5. Customize behavior in the **Settings** tab

### Adding GIFs
- **Local Files**: Use the file picker to add GIFs from your computer
- **Web Search**: Search Giphy/Tenor and download GIFs directly

### Settings
- **Display Interval**: How often GIFs appear (default: 30 minutes)
- **Display Duration**: Random range for how long GIFs show (default: 5-10 seconds)
- **Opacity**: GIF transparency level
- **Position**: Screen position for GIF display

## Project Structure

```
Glimmr/
├── src/
│   ├── main.py              # Application entry point
│   ├── gui/
│   │   ├── main_window.py   # Main application window
│   │   ├── gif_overlay.py   # GIF overlay display
│   │   └── system_tray.py   # System tray integration
│   ├── core/
│   │   ├── gif_manager.py   # GIF management logic
│   │   ├── web_search.py    # API integration for GIF search
│   │   └── config.py        # Configuration management
│   ├── utils/
│   │   └── helpers.py       # Utility functions
│   └── credentials.env      # API credentials
├── Gifs/                    # Default GIF collection
├── config.json             # User configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Icons Needed

Download and place these icons in `src/icons/`:
- `app_icon.png` (32x32) - Main application icon
- `tray_icon.png` (16x16) - System tray icon
- `play.png` (24x24) - Start/play button
- `stop.png` (24x24) - Stop button
- `add.png` (24x24) - Add GIF button
- `remove.png` (24x24) - Remove GIF button
- `search.png` (24x24) - Search button
- `settings.png` (24x24) - Settings button
- `folder.png` (24x24) - Folder/file picker button

## Configuration

The app stores user preferences in `config.json`:
```json
{
  "gif_paths": ["path/to/gif1.gif", "path/to/gif2.gif"],
  "display_interval": 1800,
  "min_display_time": 5,
  "max_display_time": 10,
  "opacity": 0.9,
  "position": "center",
  "auto_start": false
}
```

## Development

### Adding New Features
1. Core logic goes in `src/core/`
2. GUI components go in `src/gui/`
3. Utilities go in `src/utils/`

### Testing
Run the application in development mode:
```bash
python src/main.py --debug
```

## License

MIT License - Feel free to modify and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

### Common Issues
- **GIFs not displaying**: Check file paths in config.json
- **API errors**: Verify credentials.env contains valid API keys
- **Performance issues**: Reduce GIF file sizes or display frequency

### Support
Create an issue on GitHub for bug reports or feature requests.
