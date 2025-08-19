# flask server with socketio and frontend
# Production-ready Flask application

import logging
import os
import signal
import sys
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.exceptions import HTTPException

# Import eventlet for production WebSocket support
try:
    import eventlet
    eventlet.monkey_patch()
    ASYNC_MODE = 'eventlet'
except ImportError:
    ASYNC_MODE = 'threading'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# main variables
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

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

socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    logger=False, 
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
    async_mode=ASYNC_MODE
)

# Chrome DevTools endpoint (reduces log noise)
@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    return jsonify({}), 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    # Don't log Chrome DevTools requests as warnings
    if not request.path.startswith('/.well-known/appspecific/'):
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
    return jsonify({'status': 'healthy', 'environment': 'development'})

# startup
@app.route('/', methods=["GET", "POST"])
def index():
    logger.info(f"Index page accessed from {request.remote_addr}")
    return render_template('index.html')

# pipes
@socketio.on('main_socket')
def main_socket(data):
    logger.info(f"Socket message received from {request.sid}: {data}")
    try:
        emit('exchange', data, broadcast=True)
        logger.info("Message broadcasted successfully")
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        emit('error', {'message': 'Failed to broadcast message'})

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid} from {request.remote_addr}")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

# Graceful shutdown handler
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, shutting down gracefully...")
    try:
        socketio.stop()
        logger.info("SocketIO stopped gracefully")
    except Exception as e:
        logger.error(f"Error stopping SocketIO: {e}")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting Flask app on {host}:{port}")
    logger.info(f"Using async mode: {ASYNC_MODE}")
    logger.info("Press Ctrl+C to stop the server gracefully")
    
    try:
        socketio.run(app, host=host, port=port, debug=False)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down gracefully...")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)
