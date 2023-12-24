from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from video_dehazing import dehaze_video
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        uploaded_file = request.files['video']
        print("Saving")
        video_path = './to_dehaze/video.mp4'
        uploaded_file.save(video_path)

        # Perform dehazing on the uploaded video
        dehaze_video(video_path)

        # Emit a socket signal to signify that the video has been dehazed
        socketio.emit('dehazing_complete', {'message': 'Video dehazing is complete'})

        return jsonify({'message': 'Video uploaded and dehazing in progress. Check back later for the result.'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/getVideo')
def get_dehazed_video():
    try:
        dehazed_video_path = './to_dehaze/dehazed.mp4'
        return send_file(dehazed_video_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='10.0.7.46', port=5000, debug=True)



"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import Sequence
import cv2
import numpy as np
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model
import pickle
import asyncio
import matplotlib.pyplot as plt
import multiprocessing as mp
import base64
from tkinter import Tk, Label, Canvas, PhotoImage
from io import BytesIO
from PIL import Image, ImageTk


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

root = Tk()
root.title("Dehazed Frame Display")

# Image display setup
label = Label(root)
label.pack()
canvas = Canvas(root, width=480, height=360)
canvas.pack()

dehaze_model = None  # Declare dehaze_model as a global variable
dehazed_photo = None  # Reference to the PhotoImage object

def ssim_loss(y_true, y_pred):
    y_true = tf.image.convert_image_dtype(y_true, tf.float32)
    return 1 - tf.image.ssim(y_true, y_pred, max_val=1.0)

# Load the dehaze model outside the socket event handler
dehaze_model_path = './saved_models/dehaze_model.h5'
dehaze_model = tf.keras.models.load_model(dehaze_model_path, custom_objects={'ssim_loss': ssim_loss})

@socketio.on('stream')
def handle_stream(data):
    frame = data.get('frame')
    if frame:
        nparr = np.frombuffer(base64.b64decode(frame.split(',')[1]), np.uint8)
        color_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        dehaze_frame(color_image)
    else:
        print("No frame data received.")

def dehaze_frame(frame):
    global dehazed_photo  # Ensure this is a global reference
    try:
        processed_frame = cv2.resize(frame, (480, 360), interpolation=cv2.INTER_LINEAR)
        processed_frame = np.expand_dims(processed_frame, axis=0)
        dehazed_frame = dehaze_model.predict(processed_frame)
        dehazed_frame = np.squeeze(dehazed_frame, axis=0)
        
        dehazed_image = Image.fromarray((dehazed_frame * 255).astype(np.uint8))
        dehazed_photo = ImageTk.PhotoImage(dehazed_image)

        # Update the Label and Canvas with the new dehazed frame
        label.configure(image=dehazed_photo)
        label.image = dehazed_photo

        canvas.create_image(0, 0, anchor='nw', image=dehazed_photo)

        _, buffer = cv2.imencode('.jpeg', dehazed_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        socketio.emit('response', {'latency': 0, 'frame': img_base64})
    except Exception as e:
        print(f"Error dehazing frame: {e}")

if __name__ == '__main__':
    root.mainloop()
    socketio.run(app, host='10.0.7.46', port=5000, debug=True)

"""