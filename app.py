import cv2
import numpy as np
import base64
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
    process_frame(frame)

def process_frame(frame):
    # Convert the base64 encoded image to a NumPy array
    nparr = np.frombuffer(base64.b64decode(frame.split(',')[1]), np.uint8)
    
    # Decode the image using OpenCV
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    print("Image Shape:", image.shape)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate the average intensity of the grayscale image
    average_intensity = np.mean(gray_image)

    # Print the average intensity
    print("Average Intensity:", average_intensity)

    # Display the original and grayscale images using OpenCV
    cv2.imshow('Original Image', image)
    cv2.imshow('Grayscale Image', gray_image)

    # Wait for a short period (1 millisecond) to allow the images to be displayed
    cv2.waitKey(1)
    """ # Your OpenCV processing code goes here
    # For example, you can display the image using OpenCV
    cv2.imshow('Received Video Stream', image)

    cv2.waitKey(1) """

if __name__ == '__main__':
    socketio.run(app, debug=True)
