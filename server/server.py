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
    event_type = data.get('event_type')
    textLine1 = data.get('textLine1')
    textLine2 = data.get('textLine2')
    textLine3 = data.get('textLine3')
    audio_file = data.get('audioFile')

    if event_type and textLine1 and textLine2 and audio_file:
        # Emit a WebSocket event to notify the client to display the alert
        socketio.emit('display_alert', {
            'event_type': event_type,
            'textLine1': textLine1,
            'textLine2': textLine2,
            'textLine3': textLine3,
            'audioFile': audio_file
        })
        return {'status': 'success'}
    else:
        return "Missing data", 400

# Serve generatedAudio folder
@app.route('/generatedAudio/<path:filename>')
def audio(filename):
    return send_from_directory('../generatedAudio', filename)
