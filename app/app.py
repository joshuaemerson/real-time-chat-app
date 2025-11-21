import logging
import os
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import redis


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configure Redis
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_client = redis.Redis(host=redis_host, 
                           port=redis_port, 
                           decode_responses=True)

# Init SocketIO with Redis message queue
socketio = SocketIO(app, 
                    cors_allowed_origins="*", 
                    message_queue=f'redis://{redis_host}:{redis_port}')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store active users (in-memory, per instance)
active_users = {} # maps sessionID (sid) to usernames

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    try:
        redis_client.ping()
        return jsonify({'status': 'healthy', 
                        'redis': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 
                        'error': str(e)}), 503

@socketio.on('connect')
def handle_connect():
    logger.info(f'Client connected: {request.sid}')
    emit('system_message', 
         {'msg': 'Connected to the chat server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')
    if request.sid in active_users:
        username = active_users[request.sid]
        del active_users[request.sid]
        emit('user_left', 
             {'username': username}, 
             broadcast=True)

@socketio.on('join')
def handle_join(data):
    username = data.get('username', 'Anonymous')
    room = data.get('room', 'general')

    active_users[request.sid] = username
    join_room(room)

    logger.info(f'{username} joined room {room}')
    emit('system_message', 
         {'msg': f'You joined room: {room}'}, 
         room=request.sid) # private message to user
    emit('user_joined', 
         {'username': username, 'room': room}, 
         room=room, 
         skip_sid=request.sid)

    # Send current user count
    user_count = len(active_users)
    emit('user_count', 
         {'count': user_count}, 
         broadcast=True)

@socketio.on('leave')
def handle_leave(data):
    username, room = data.get('username', 'Anonymous')
    room = data.get('room', 'general')

    leave_room(room)
    logger.info(f'{username} left room {room}')
    emit('user_left', 
         {'username': username, 'room': room}, 
         room=room)

@socketio.on('message')
def handle_message(data):
    username = data.get('username', 'Anonymous')
    room = data.get('room', 'general')
    message = data.get('message', '')

    if message.strip():
        logger.info(f'Message from {username} in {room}: {message}')
        emit('message', {
            'username': username,
            'message': message,
            'room': room
        }, room=room)

@socketio.on('typing')
def handle_typing(data):
    username = active_users.get(request.sid, 'Anonymous')
    room = data.get('room', 'general')
    emit('typing', 
         {'username': username}, 
         room=room, 
         skip_sid=request.sid)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
