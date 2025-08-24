# Flask + DearPyGUI Server
# Cross-platform server with integrated web and desktop GUI interfaces

import logging
import os
import signal
import sys
import time
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Global variables for GUI communication
server_status = "running"
gui_ready = False
dpg_context = None

# Security headers
@app.after_request
def add_security_headers(response):
    security_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }
    for header, value in security_headers.items():
        response.headers[header] = value
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error for path: {request.path} from {request.remote_addr}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'environment': 'development',
        'gui_status': server_status,
        'gui_ready': gui_ready
    })

# Main page
@app.route('/', methods=["GET", "POST"])
def index():
    logger.info(f"Index page accessed from {request.remote_addr}")
    return render_template('index.html')

# Server status endpoint
@app.route('/status')
def server_status_endpoint():
    return jsonify({
        'web_server': 'running',
        'gui_app': server_status,
        'gui_ready': gui_ready,
        'timestamp': time.time()
    })

# GUI control endpoints
@app.route('/gui/start', methods=['POST'])
def start_gui():
    global server_status
    server_status = "running"
    return jsonify({'status': 'success', 'message': 'GUI is running'})

@app.route('/gui/stop', methods=['POST'])
def stop_gui():
    global server_status
    server_status = "stopping"
    return jsonify({'status': 'success', 'message': 'GUI stopping'})

def create_gui():
    """Create the DearPyGUI application"""
    global gui_ready, dpg_context
    
    try:
        import dearpygui.dearpygui as dpg
        
        logger.info("Creating DearPyGUI application...")
        
        # Initialize DearPyGUI
        dpg.create_context()
        dpg.create_viewport(title="Flask + DearPyGUI Server", width=800, height=600)
        
        # Create main window
        with dpg.window(label="Server Control", width=780, height=580):
            dpg.add_text("Flask + DearPyGUI Server")
            dpg.add_separator()
            
            # Server info
            with dpg.group(horizontal=True):
                dpg.add_text("Web Server:")
                dpg.add_text("Running", color=(0, 255, 0))
            
            with dpg.group(horizontal=True):
                dpg.add_text("GUI Status:")
                status_text = dpg.add_text(server_status, color=(0, 255, 0))  # Green for running
            
            dpg.add_separator()
            
            # Control buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Refresh Status", callback=update_gui_status, user_data=status_text)
                dpg.add_button(label="Open Web Interface", callback=open_web_interface)
                dpg.add_button(label="Server Info", callback=show_server_info)
            
            dpg.add_separator()
            
            # Log display
            dpg.add_text("Server Log:")
            log_text = dpg.add_text("", wrap=700)
            
            # Update log periodically
            def update_log():
                if dpg.does_item_exist(log_text):
                    dpg.set_value(log_text, f"Last update: {time.strftime('%H:%M:%S')} - Server running on port 5000")
            
            # Set up periodic updates using a timer
            dpg.set_frame_callback(frame=0, callback=update_log)
        
        gui_ready = True
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        return dpg
        
    except ImportError:
        logger.error("DearPyGUI not installed. Please install with: pip install dearpygui")
        gui_ready = False
        return None
    except Exception as e:
        logger.error(f"Error creating GUI: {e}")
        gui_ready = False
        return None

def update_gui_status(sender, app_data, user_data):
    """Update GUI status display"""
    if dpg_context and dpg_context.does_item_exist(user_data):
        dpg_context.set_value(user_data, server_status)
        # Update color based on status
        if server_status == "running":
            dpg_context.configure_item(user_data, color=(0, 255, 0))  # Green
        elif server_status == "stopping":
            dpg_context.configure_item(user_data, color=(255, 165, 0))  # Orange
        elif server_status == "stopped":
            dpg_context.configure_item(user_data, color=(255, 0, 0))  # Red
        else:
            dpg_context.configure_item(user_data, color=(255, 255, 0))  # Yellow

def open_web_interface():
    """Open web interface in default browser"""
    import webbrowser
    webbrowser.open('http://localhost:5000')

def show_server_info():
    """Show server information in GUI"""
    if dpg_context:
        with dpg_context.window(label="Server Information", width=400, height=300):
            dpg_context.add_text(f"Flask Version: {Flask.__version__}")
            dpg_context.add_text(f"Python Version: {sys.version}")
            dpg_context.add_text(f"Server Port: 5000")
            dpg_context.add_text(f"Host: 0.0.0.0")

def run_integrated_server():
    """Run Flask and DearPyGUI together"""
    global dpg_context, server_status, http_server
    
    # Create GUI
    dpg_context = create_gui()
    if not dpg_context:
        logger.error("Failed to create GUI, running Flask only")
        return False
    
    # Start Flask in a way that works with DearPyGUI
    from werkzeug.serving import make_server
    from threading import Thread
    
    # Create WSGI server
    http_server = make_server('0.0.0.0', 5000, app)
    
    # Start Flask server in background thread
    def run_flask():
        logger.info("Starting Flask server on 0.0.0.0:5000")
        http_server.serve_forever()
    
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Main GUI loop with Flask integration
    logger.info("Starting integrated Flask + DearPyGUI server")
    
    try:
        while dpg_context.is_dearpygui_running() and server_status != "stopping":
            dpg_context.render_dearpygui_frame()
            time.sleep(0.01)
            
            # Check if Flask server is still running
            if not flask_thread.is_alive():
                logger.error("Flask server thread died")
                break
                
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        # Cleanup
        logger.info("Shutting down Flask + DearPyGUI server")
        if 'http_server' in globals():
            http_server.shutdown()
        if dpg_context:
            dpg_context.destroy_context()
        server_status = "stopped"
        gui_ready = False
    
    return True

# Graceful shutdown handler
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, shutting down gracefully")
    global server_status
    server_status = "stopping"
    time.sleep(1)
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting Flask + DearPyGUI server on {host}:{port}")
    logger.info("Press Ctrl+C to stop the server gracefully")
    
    try:
        success = run_integrated_server()
        if not success:
            logger.error("Failed to start Flask + DearPyGUI server")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down gracefully")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"Error starting integrated server: {e}")
        sys.exit(1)
