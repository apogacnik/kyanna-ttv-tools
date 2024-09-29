from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# Serve test html
@app.route('/')
def overlay():
    return render_template('index.html')

# Serve alert page for OBS overlay
@app.route('/alert', methods=['GET'])
def alerts_get():
    return render_template('alert.html')

# Handle post requests (new alerts)
@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    username = data.get('username')
    audio_file = data.get('audioFile')

    if username and audio_file:
        # Emit a WebSocket event to notify the client to display the alert
        socketio.emit('display_alert', {'username': username, 'audio_file': audio_file})
        return {'status': 'success'}
    else:
        return "Missing data", 400

# Serve generatedAudio folder
@app.route('/generatedAudio/<path:filename>')
def audio(filename):
    return send_from_directory('../generatedAudio', filename)
