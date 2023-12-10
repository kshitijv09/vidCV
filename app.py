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



""" @app.route('/')
def index():
    return render_template('index.html') """

@socketio.on('stream')
def handle_stream(data):
    frame = data['frame']
    print("Frame is ",frame)
    process_frame(frame)

def process_frame(frame):

    start_time= time.time()
    # Convert the base64 encoded image to a NumPy array
    nparr = np.frombuffer(base64.b64decode(frame.split(',')[1]), np.uint8)
    print(nparr)
    # Decode the image using OpenCV
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #cv2.imshow('Server Image', image)
   
    cv2.waitKey(1000)

    #print("Image Shape:", image.shape)

   
    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    print("Encoded ",encoded_image)
    end_time = time.time()

    # Calculate and print the latency
    latency = end_time - start_time
    print("Latency:", latency, "seconds")

    socketio.emit('response', {'latency': latency, 'frame': encoded_image})
   

if __name__ == '__main__':
    socketio.run(app, debug=True)
