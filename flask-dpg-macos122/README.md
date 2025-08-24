# Flask + DearPyGUI Server

A cross-platform integrated server that runs Flask web server and DearPyGUI desktop application in harmony, providing seamless web and desktop interfaces for server control and monitoring.

## Features

- 🌐 **Flask Web Server** - RESTful API endpoints and web interface
- 🖥️ **DearPyGUI Desktop App** - Native desktop interface for server control
- 🔄 **Integrated Operation** - Web server and GUI run in harmony
- 🚀 **Cross-Platform** - Works on Windows, macOS, and Linux
- 🎯 **Minimal Dependencies** - Only essential packages included
- 🔧 **Auto-Setup** - Automated virtual environment and dependency installation

## Architecture

The server runs as an integrated application:

1. **Main Application** (Main Thread)
   - DearPyGUI desktop interface
   - Server control and monitoring
   - Real-time status updates

2. **Flask Web Server** (Background Thread)
   - REST API endpoints
   - Web interface for remote control
   - Health monitoring
   - Seamlessly integrated with GUI

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation & Run

1. **Navigate to the folder**
   ```bash
   cd flask-dpg
   ```

2. **Run the build script**
   ```bash
   ./build.sh
   ```

   The script will:
   - Detect your operating system
   - Create a Python virtual environment
   - Install all required dependencies
   - Start the integrated server with both web and desktop interfaces

3. **Access the interfaces**
   - **Web Interface**: http://localhost:5000
   - **Desktop GUI**: Opens automatically in a new window

## Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

## API Endpoints

- `GET /` - Main web interface
- `GET /health` - Server health check
- `GET /status` - Current server and GUI status
- `POST /gui/start` - Start the desktop GUI
- `POST /gui/stop` - Stop the desktop GUI

## Web Interface

The web interface provides:
- Real-time server status monitoring
- GUI control buttons (start/stop)
- Server information display
- Auto-refresh every 5 seconds

## Desktop GUI

The integrated DearPyGUI application shows:
- Server status indicators
- Control buttons
- Real-time log updates
- Server information
- Direct integration with web server

## Project Structure

```
flask-dpg/
├── app.py              # Main Flask + DearPyGUI server
├── requirements.txt    # Python dependencies
├── build.sh           # Cross-platform setup script
├── templates/         # HTML templates
│   └── index.html    # Web interface
├── static/            # Static assets (CSS, JS)
└── venv/              # Virtual environment (auto-created)
```

## Dependencies

- **Flask** - Web framework
- **DearPyGUI** - Desktop GUI framework
- **Werkzeug** - WSGI utilities
- **Jinja2** - Template engine

## Cross-Platform Support

### Windows
- Git Bash, PowerShell, or Command Prompt
- Virtual environment activation: `venv\Scripts\activate`

### macOS
- Terminal or iTerm2
- Virtual environment activation: `source venv/bin/activate`

### Linux
- Terminal
- Virtual environment activation: `source venv/bin/activate`

## Usage Examples

### Starting the Server
```bash
./build.sh
```

### Controlling GUI from Web
1. Open http://localhost:5000
2. Click "Start GUI" to launch desktop app
3. Click "Stop GUI" to close desktop app
4. Use "Refresh Status" to update information

### Programmatic Control
```bash
# Start GUI
curl -X POST http://localhost:5000/gui/start

# Stop GUI
curl -X POST http://localhost:5000/gui/stop

# Check status
curl http://localhost:5000/status
```

## Troubleshooting

### Common Issues

- **DearPyGUI not found**: Ensure you're in the virtual environment
- **Port already in use**: Change the port in `app.py` or set `PORT` environment variable
- **Permission denied**: Make sure `build.sh` is executable (`chmod +x build.sh`)

### Debug Mode

For debugging, modify `app.py`:
```python
# Change debug=False to debug=True in the Flask run call
app.run(host=host, port=port, debug=True, use_reloader=False)
```

## Customization

### Adding New Endpoints
```python
@app.route('/api/custom')
def custom_endpoint():
    return jsonify({'message': 'Custom endpoint'})
```

### Modifying GUI
Edit the `run_gui()` function in `app.py` to customize the desktop interface.

### Changing Port
Set the `PORT` environment variable or modify the default in `app.py`.

## License

This template is part of the server-templates repository.

## Contributing

Feel free to submit issues and enhancement requests!
