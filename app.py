import cv2
import numpy as np
import base64 
import time

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")



@app.route('/')
def index():
    return render_template('index.html') 

@socketio.on('stream')
def handle_stream(data):
    frame = data['frame']
    #print("Frame is ",frame)
    process_frame(frame)

import time
import base64
import numpy as np
import cv2

def process_frame(frame):
    start_time = time.time()

    # Convert the base64 encoded image to a NumPy array
    nparr = np.frombuffer(base64.b64decode(frame.split(',')[1]), np.uint8)

    # Decode the image using OpenCV
    color_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert the color image to grayscale
    gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

    # Encode the grayscale image
    _, buffer = cv2.imencode('.jpg', gray_image, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    end_time = time.time()

    # Calculate and print the latency
    latency = end_time - start_time

    # Emit the response to the client
    socketio.emit('response', {'latency': latency, 'frame': encoded_image})

   

if __name__ == '__main__':
    socketio.run(app, debug=True)




















""" from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import io

app = Flask(__name__)
CORS(app)

def process_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Perform some operation on the frame (e.g., convert to grayscale)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frames.append(gray_frame)

    cap.release()
    return frames

@app.route('/', methods=['POST'])
def upload():
    try:
        # Check if the 'video' file is present in the request
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        video_file = request.files['video']

        # Save the video file to a temporary location
        video_path = '/home/kshitijv09/mern/vidml/video.mp4'
        video_file.save(video_path)

        # Process frames
        frames = process_frames(video_path)

        print("Frames processed successfully!")

        # Encode frames into a video file
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        height, width = frames[0].shape
        out = cv2.VideoWriter('/home/kshitijv09/mern/vidml/processed_video.mp4', fourcc, 20.0, (width, height))

        for frame in frames:
            out.write(cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

        out.release()

        # Send the processed video file as a response
         return send_file('/home/kshitijv09/mern/vidml/processed_video.mp4', as_attachment=False) 
        with open('/home/kshitijv09/mern/vidml/processed_video.mp4', 'rb') as video_file:
            video_data = video_file.read()

        # Send the processed video file as part of the response
        return video_data, 200, {'Content-Type': 'video/mp4'}

    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) """
























""" import cv2
from flask import Flask, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

# Initialize camera (adjust the index if needed)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

@app.route('/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True) """






















