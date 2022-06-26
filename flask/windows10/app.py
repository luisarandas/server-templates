

# luis arandas 26-06-2022
# flask server with socketio to the frontend

from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from random import random





# start main variables
app = Flask(__name__, static_folder='static')
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

# startup i guess
@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    socketio.run(app, debug=False)
