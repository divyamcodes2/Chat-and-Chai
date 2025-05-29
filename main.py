# Imports here
import os
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix

# Config logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# App Configuration Settings


class Config:
    """Application configuration with secure defaults"""
    # If the first part (os.environ.get('SECRET_KEY')) is empty or None, the second part (os.urandom(24)) is used instead.
    # os.urandom(24) generates 24 random bytes (192 bits) of cryptographically secure random data.
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    # Gets environment variable value: os.environ.get("FLASK_DEBUG", "False") retrieves the value of the FLASK_DEBUG environment variable. If it's not set, it defaults to "False".
    # Converts to lowercase: .lower() converts the retrieved value to lowercase, so the comparison is case-insensitive.
    # Checks for truthy values: in ("true", "1", "t")
    DEBUG = os.environ.get(
        'FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

    # This will allow to get request from almost any origin
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    # Available chat rooms - stored as constant for now, could be moved to database
    CHAT_ROOMS = [
        'ASCII Me Anything',
        '404 Not Found',
        'No Typo Zone',
        'Byte Me'
    ]


# Initialize Flask app
app = Flask(__name__)
# This line of code is typically used in a Flask application to load configuration settings from a separate module or class.
app.config.from_object(Config)

# Handle reverse proxy headers -:
# x_proto: Trust the X-Forwarded-Proto header to determine the original protocol used by the client.
# x_host: Trust the X-Forwarded-Host header to determine the original host requested by the client.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize SocketIO with appropriate CORS settings
# This line sets the cors_allowed_origins parameter from config.
# Enable logging of CORS-related events
# Enable logging of Engine.IO events, such as WebSocket connections and messages
socketio = SocketIO(
    app,
    cors_allowed_origins=app.config['CORS_ORIGINS'],
    logger=True,
    engineio_logger=True
)

# In-memory storage for active users
# In production, consider using Redis or another distributed storage
# Dict[str, dict]: The keys are socket IDs (sids), values are dictionaries of user info
active_users: Dict[str, dict] = {}


def generate_guest_username() -> str:
    """Generate a unique guest username with timestamp to avoid collisions"""
    # In inside it is nothing but stores a string
    timestamp = datetime.now().strftime('%H%M')
    return f'Guest{timestamp}{random.randint(1000, 9999)}'


@app.route('/')
def index():
    # If the key 'username' is not present in the session, then generate one
    if 'username' not in session:
        session['username'] = generate_guest_username()
        logger.info(f"New user session created: {session['username']}")

    # The rooms variable contains the list of chat rooms which is set up inside the class
    return render_template(
        'index.html',
        username=session['username'],
        rooms=app.config['CHAT_ROOMS']
    )


# Making a connection -:
@socketio.event
def connect():
    try:
        # We are creating the username if the user is not present in the dictionary
        if 'username' not in session:
            session['username'] = generate_guest_username()

        # We are adding the username and the time at which the user joined to the dictionary
        # The full form of sid is socket id or session id
        active_users[request.sid] = {
            'username': session['username'],
            'connected_at': datetime.now().isoformat()
        }

        # Sending the updated list of active users
        emit('active_users', {
            'users': [user['username'] for user in active_users.values()]
        }, broadcast=True)

        logger.info(f"User connected: {session['username']}")

    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return False


# Disconnecting the user -:
@socketio.event
def disconnect():
    try:
        # Fetching the username of the user
        if request.sid in active_users:
            username = active_users[request.sid]['username']
            # Deleting the user from the dictionary for getting disconnected
            del active_users[request.sid]

            # Sending the updated list of active users
            emit('active_users', {
                'users': [user['username'] for user in active_users.values()]
            }, broadcast=True)

            logger.info(f"User disconnected: {username}")

    except Exception as e:
        logger.error(f"Disconnection error: {str(e)}")


# Joining the room -:
@socketio.on('join')
def on_join(data: dict):
    try:
        # This line retrieves the username of the current user from the session dictionary
        username = session['username']
        # This line retrieves the room name from the data dictionary
        room = data['room']

        # This line checks if the room name is in the list of available chat rooms
        if room not in app.config['CHAT_ROOMS']:
            logger.warning(f"Invalid room join attempt: {room}")
            return

        # This line joins the user to the specified room
        join_room(room)
        # This line updates the active_users dictionary to store the room name
        active_users[request.sid]['room'] = room

        # This line emits a status event to all users in the same room
        emit('status', {
            'msg': f'{username} has joined the room.',
            'type': 'join',
            'timestamp': datetime.now().isoformat()
        }, room=room)

        logger.info(f"User {username} joined room: {room}")

    except Exception as e:
        logger.error(f"Join room error: {str(e)}")


# Leave the room -:
@socketio.on('leave')
def on_leave(data: dict):
    try:
        # Retrieve username and room name
        username = session['username']
        room = data['room']

        # This line leaves the user from the specified room
        leave_room(room)
        # This line checks if the request.sid is present in the active_users dictionary
        if request.sid in active_users:
            # This is calling the pop method which removes and returns the value associated with 'room'
            active_users[request.sid].pop('room', None)

        # This line emits a status event to all users in the same room
        emit('status', {
            'msg': f'{username} has left the room.',
            'type': 'leave',
            'timestamp': datetime.now().isoformat()
        }, room=room)

        logger.info(f"User {username} left room: {room}")

    except Exception as e:
        logger.error(f"Leave room error: {str(e)}")


# Handling Messages -:
@socketio.on('message')
def handle_message(data: dict):
    try:
        username = session['username']

        # Get the room name (default to 'General')
        room = data.get('room', 'General')
        # Get the message type (default to 'message')
        msg_type = data.get('type', 'message')
        # Get the actual message, strip whitespace
        message = data.get('msg', '').strip()

        # If message is empty, return
        if not message:
            return

        timestamp = datetime.now().isoformat()

        # For private chatting
        if msg_type == 'private':
            # This line retrieves the target user
            target_user = data.get('target')
            # If target user is not present, return
            if not target_user:
                return

            # Iterate over all active users in the chat application
            for sid, user_data in active_users.items():
                # This line checks if the username in user_data is equal to the target user
                if user_data['username'] == target_user:
                    # Send the private message only to the target
                    emit('private_message', {
                        'msg': message,
                        'from': username,
                        'to': target_user,
                        'timestamp': timestamp
                    }, room=sid)
                    logger.info(
                        f"Private message sent: {username} -> {target_user}")
                    return

            logger.warning(
                f"Private message failed - user not found: {target_user}")

        else:
            # If the message type is not private then everybody can see the message
            # Check if the room is valid
            if room not in app.config['CHAT_ROOMS']:
                logger.warning(f"Message to invalid room: {room}")
                return

            # Emit the message to all users in the room
            emit('message', {
                'msg': message,
                'username': username,
                'room': room,
                'timestamp': timestamp
            }, room=room)

            logger.info(f"Message sent in {room} by {username}")

    except Exception as e:
        logger.error(f"Message handling error: {str(e)}")


if __name__ == '__main__':
    # In production, use gunicorn or uwsgi instead
    port = int(os.environ.get('PORT', 5000))
    # This flag essentially tells Flask-SocketIO to ignore the warning and continue running the development server.
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG'],
        use_reloader=app.config['DEBUG'],
        allow_unsafe_werkzeug=True
    )
