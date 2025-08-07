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
## App Feature Screenshots

Showcase the main features of your app with screenshots here.  
**Tip:** Replace the placeholder text below with your actual images.

### Homepage
_Add a screenshot of the homepage here_
![Homepage Screenshot]<img width="1918" height="1078" alt="Home" src="https://github.com/user-attachments/assets/c9e50186-bbe1-4e9d-a1ef-6bcca8f1f4d4" />


### Library
_Add a screenshot of the library feature here_
![Library Screenshot]<img width="1917" height="1078" alt="Library" src="https://github.com/user-attachments/assets/9998a218-ff03-47d4-a2c6-677fd9997fce" />


### Search
_Add a screenshot of the search feature here_
![Search Screenshot]<img width="1918" height="1078" alt="Search" src="https://github.com/user-attachments/assets/381958ac-584b-49cb-a20c-350e6fb4aa52" />


### Settings
_Add a screenshot of the settings page here_
![Settings Screenshot]
<img width="1918" height="1078" alt="Setting" src="https://github.com/user-attachments/assets/7c6e4048-aa43-4a57-a9cf-5949baecfdc3" />

---

## Working Demo Screenshots

Show how the app looks and works in action.

### Demo 1:
_A working demo screenshot or animated GIF here_
![Demo Screenshot]
<img width="1918" height="1078" alt="demo" src="https://github.com/user-attachments/assets/8a621ecb-9c7b-4fb3-8a67-7d842112fe71" />

### Demo 2:
_Another demo screenshot or animated GIF here_
![Demo Screenshot]<img width="1918" height="1078" alt="demo1" src="https://github.com/user-attachments/assets/2f3d87d6-3d39-4fc0-8a60-b85b6c53845f" />

### Demo 3:
_Another demo screenshot or animated GIF here_
![Demo Screenshot]<img width="1918" height="1078" alt="demo2" src="https://github.com/user-attachments/assets/0256faf8-85fd-455a-9575-dfa6a8758c75" />

### Demo 4: 
_Another demo screenshot or animated GIF here_
![Demo Screenshot]<img width="1912" height="1077" alt="demo3" src="https://github.com/user-attachments/assets/e6d86dda-75c2-45ae-ab56-04e4ac794452" />


### Demo 5: 
_Another demo screenshot or animated GIF here_
![Demo Screenshot]<img width="1918" height="1078" alt="demo4" src="https://github.com/user-attachments/assets/c77eafac-4b90-474a-aa03-2983e5b839fd" />

### Demo 6: 
_Another demo screenshot or animated GIF here_
![Demo Screenshot]<img width="1918" height="1078" alt="demo5" src="https://github.com/user-attachments/assets/2f65008f-040b-48db-bbdc-acb736c16c94" />

### Demo 7: 
_Another demo screenshot or animated GIF here_
![Demo Screenshot]<img width="1918" height="1078" alt="demo6" src="https://github.com/user-attachments/assets/72fc6e41-94d6-4e82-ac6f-f79090ecae7a" />


### Demo 8: 
_Another demo screenshot or animated GIF here_
![Demo Screenshot]<img width="1918" height="1078" alt="demo7" src="https://github.com/user-attachments/assets/8202ec10-e994-46ff-8d22-4b551602ff79" />





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

