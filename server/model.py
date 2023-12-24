import tensorflow as tf
from tensorflow.keras.regularizers import l2
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

tf.keras.backend.clear_session()

print("Num GPUs Available:", len(tf.config.experimental.list_physical_devices('GPU')))

# Data Augmentation

class CustomDataGenerator(Sequence):
    def __init__(self, data_dir, image_size=(480, 360), batch_size=1, mode='train'):
        self.data_dir = data_dir
        self.image_size = image_size
        self.batch_size = batch_size
        self.mode = mode
        self.hazy_dir = os.path.join(self.data_dir, f'hazy')
        self.gt_dir = os.path.join(self.data_dir, f'GT')
        self.hazy_images = os.listdir(self.hazy_dir)
        self.gt_images = os.listdir(self.gt_dir)
        self.indexes = np.arange(len(self.hazy_images))
        self.seed = 42  
        self.datagen = ImageDataGenerator(
            rescale=1.0 / 255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True
        )

    def __len__(self):
        return int(np.ceil(len(self.hazy_images) / float(self.batch_size)))

    def __getitem__(self, index):
        batch_indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]
        np.random.shuffle(batch_indexes)
        batch_hazy = []
        batch_gt = []

        for i in batch_indexes:
            hazy_path = os.path.join(self.hazy_dir, self.hazy_images[i])
            gt_path = os.path.join(self.gt_dir, self.gt_images[i])

            hazy_img = cv2.imread(hazy_path)
            gt_img = cv2.imread(gt_path)

            hazy_img = cv2.cvtColor(hazy_img, cv2.COLOR_BGR2RGB) 
            gt_img = cv2.cvtColor(gt_img, cv2.COLOR_BGR2RGB)

            hazy_img = cv2.resize(hazy_img, self.image_size, interpolation=cv2.INTER_LINEAR)
            gt_img = cv2.resize(gt_img, self.image_size, interpolation=cv2.INTER_LINEAR)

            batch_hazy.append(hazy_img)
            batch_gt.append(gt_img)

        return np.array(batch_hazy), np.array(batch_gt)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n >= len(self):
            raise StopIteration
        batch_x, batch_y = self.__getitem__(self.n)
        self.n += 1

        augmented_batch_x = self.datagen.flow(batch_x, batch_size=len(batch_x), shuffle=False, seed=self.seed)
        augmented_batch_y = self.datagen.flow(batch_y, batch_size=len(batch_y), shuffle=False, seed=self.seed)

        return next(augmented_batch_x), next(augmented_batch_y)
    
# Batch generation
   
train_generator = CustomDataGenerator('reside indoor/train', mode='train')
validation_generator = CustomDataGenerator('reside indoor/train', mode='validation')
test_generator = CustomDataGenerator('reside indoor/test', mode='test')

# Main Model

def Model_(input_shape=(360, 480, 3)):
    input_img = Input(shape=input_shape)
    
    x1 = Conv2D(32, (3, 3), padding='same')(input_img)
    x1 = BatchNormalization()(x1)
    x1 = LeakyReLU(alpha=0.1)(x1)
    x1_pool = MaxPooling2D((2, 2), padding='same')(x1)
    
    x2 = Conv2D(64, (3, 3), padding='same')(x1_pool)
    x2 = BatchNormalization()(x2)
    x2 = LeakyReLU(alpha=0.1)(x2)
    x2_pool = MaxPooling2D((2, 2), padding='same')(x2)
    
    x3 = Conv2D(128, (3, 3), padding='same')(x2_pool)
    x3 = BatchNormalization()(x3)
    x3 = LeakyReLU(alpha=0.1)(x3)
    encoded = MaxPooling2D((2, 2), padding='same')(x3)
    
    x = Conv2D(128, (3, 3), padding='same')(encoded)
    x = LeakyReLU(alpha=0.1)(x)
    
    x = Conv2DTranspose(64, (3, 3), strides=(1, 1), padding='same')(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Conv2DTranspose(64, (3, 3), strides=(2, 2), padding='same')(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Concatenate()([x, x3])
    
    x = Conv2DTranspose(32, (3, 3), strides=(1, 1), padding='same')(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Conv2DTranspose(32, (3, 3), strides=(2, 2), padding='same')(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Concatenate()([x, x2])
    
    x = Conv2DTranspose(16, (3, 3), strides=(1, 1), padding='same')(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Conv2DTranspose(16, (3, 3), strides=(2, 2), padding='same')(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Concatenate()([x, x1])
    
    decoded = Conv2D(3, (3, 3), padding='same')(x) 
    autoencoder = Model(input_img, decoded)
    
    return autoencoder

# Training the Model

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',  # Metric to be monitored
    factor=0.1,           # Factor by which the learning rate will be reduced (new_lr = lr * factor)
    patience=5,           # Number of epochs with no improvement after which learning rate will be reduced
    min_lr=1e-6,          # Lower bound on the learning rate
    verbose=1             # Prints a message if the learning rate is reduced
)

def ssim_loss(y_true, y_pred):
    y_true = tf.image.convert_image_dtype(y_true, tf.float32)
    return 1 - tf.image.ssim(y_true, y_pred, max_val=1.0)

with tf.device('/GPU:0'):
    dehaze_model = Model_()
    dehaze_model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001),
                                    loss=[ssim_loss, 'mse'], loss_weights=[0.75, 0.25])
    checkpoint_filepath = 'model_checkpoints/dehaze_checkpoint.h5'
    dehaze_model.load_weights(checkpoint_filepath)
    model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_filepath,
        save_weights_only=True,
        monitor='val_loss',
        mode='min',
        save_best_only=True
    )

    history = dehaze_model.fit(
        train_generator,
        initial_epoch=15,
        epochs=20,
        validation_data=validation_generator,
        callbacks=[model_checkpoint_callback, reduce_lr]
    )
    with open('training_history_2.pkl', 'wb') as file:
        pickle.dump(history.history, file)

    dehaze_model.save('saved_models/dehaze_model.h5') 
