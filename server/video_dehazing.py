import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import Sequence
import cv2
import numpy as np
import os
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model
import pickle
import asyncio
import matplotlib.pyplot as plt
import multiprocessing as mp

def dehaze_frame(frame):
    def ssim_loss(y_true, y_pred):
        y_true = tf.image.convert_image_dtype(y_true, tf.float32)
        return 1 - tf.image.ssim(y_true, y_pred, max_val=1.0)
    try:
        dehaze_model = tf.keras.models.load_model('./saved_models/dehaze_model.h5', custom_objects={'ssim_loss': ssim_loss})

        processed_frame =  cv2.resize(frame, (480, 360), interpolation=cv2.INTER_LINEAR)
        print("Resized frame shape:", processed_frame.shape)

        """ processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        print("Converted to RGB color space. Frame shape:", processed_frame.shape)
 """
        processed_frame = np.expand_dims(processed_frame, axis=0)
        print("Expanded dimensions. Frame shape:", processed_frame.shape)

        dehazed_frame =  dehaze_model.predict(processed_frame)
        dehazed_frame = np.squeeze(dehazed_frame, axis=0)
        print("Dehazed frame shape:", dehazed_frame.shape)


        #print("Dehazed frame here is ", dehazed_frame)

       
        print("Processed frame min value:", np.min(processed_frame))
        print("Processed frame max value:", np.max(processed_frame))

        print("Dehazed frame min value:", np.min(dehazed_frame))
        print("Dehazed frame max value:", dehazed_frame)  

        return dehazed_frame
    except Exception as e:
        print(f"Error dehazing frame: {e}")
        return None

def process_frames(frames):
    try:
        pool = mp.Pool(mp.cpu_count())  # Use the number of available CPU cores
        print(1)
        # Use map to parallelize the frame processing across multiple processes
        processed_frames = pool.map(dehaze_frame, frames)
        pool.close()
        pool.join()
    except Exception as e:
        print(f"Error processing frame: {e}")
        return None
    
    return processed_frames

def dehaze_video(video_path):
    video_capture = cv2.VideoCapture(video_path)
    
    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    
    frames = []
    
    success, frame = video_capture.read()
    while success:
        frames.append(frame)
        success, frame = video_capture.read()
    
    video_capture.release()
    
    chunked_frames = [frames[i:i + 10] for i in range(0, len(frames), 10)]  # Change chunk size as needed
    
    processed_frames = []
    for chunk in chunked_frames:
        processed_frames.extend(process_frames(chunk))
    
    scaled_frames = []
    for frame in processed_frames:
        scaled_frame = (frame - np.min(frame)) / (np.max(frame) - np.min(frame)) * 255
        scaled_frames.append(scaled_frame.astype(np.uint8))
    
    output_video_path = './to_dehaze/dehazed.mp4'
    video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (480, 360))

    for frame in scaled_frames:
        video_writer.write(frame)

    video_writer.release()
    print(f"Dehazed video saved: {output_video_path}")

dehaze_video('./to_dehaze/video.mp4')



""" import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import Sequence
import cv2
import numpy as np
import os
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model
import pickle
import asyncio
import matplotlib.pyplot as plt
import multiprocessing as mp

async def dehaze_frame(frame):
    def ssim_loss(y_true, y_pred):
        y_true = tf.image.convert_image_dtype(y_true, tf.float32)
        return 1 - tf.image.ssim(y_true, y_pred, max_val=1.0)
    try:
        dehaze_model = tf.keras.models.load_model('./saved_models/dehaze_model.h5', custom_objects={'ssim_loss': ssim_loss})

        processed_frame = cv2.resize(frame, (480, 360), interpolation=cv2.INTER_LINEAR)
#         processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        processed_frame = np.expand_dims(processed_frame, axis=0)

        dehazed_frame = dehaze_model.predict(processed_frame)

        dehazed_frame = np.squeeze(dehazed_frame, axis=0)
        
        return dehazed_frame
    except Exception as e:
        print(f"Error dehazing frame: {e}")
        return None

async def process_frames(frames):
    tasks = []
    for frame in frames:
        task = asyncio.create_task(dehaze_frame(frame))
        tasks.append(task)
    processed_frames = await asyncio.gather(*tasks)
    return processed_frames

async def dehaze_video(video_path):
    video_capture = cv2.VideoCapture(video_path)
    
    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    
    frames = []
    
    success, frame = video_capture.read()
    while success:
        frames.append(frame)
        success, frame = video_capture.read()
    
    video_capture.release()
    
    processed_frames = await process_frames(frames)
    scaled_frames = []
    for frame in processed_frames:
        scaled_frame = (frame - np.min(frame)) / (np.max(frame) - np.min(frame)) * 255
        scaled_frames.append(scaled_frame.astype(np.uint8))

    output_video_path = './to_dehaze/dehazed.mp4'
    video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (480, 360))

    for frame in scaled_frames:
        video_writer.write(frame)

    video_writer.release()
    print(f"Dehazed video saved: {output_video_path}")
    
    
    await dehaze_video('./to_dehaze/video.mp4') """