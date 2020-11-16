from django.db import models

from django.utils import timezone
from django.core.files.storage import FileSystemStorage



from keras.models import load_model
from keras.preprocessing import image
import json
from tensorflow import Graph
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB6
from tensorflow import keras
from tensorflow.keras.models import Model
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import Input, Dense, BatchNormalization, Dropout, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
import os, cv2


ROWS = 256
COLS = 256
Channel = 3


#
model_graph = Graph()
with model_graph.as_default():
    tf_session = tf.compat.v1.Session()
    with tf_session.as_default():
        # create the base pre-trained model
        base_model = EfficientNetB6(weights='imagenet', include_top=False, input_tensor=Input(shape=(ROWS, COLS, 3)))
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        # # let's add a fully-connected layer
        x = Dense(2024, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)
        x = Dense(512, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)
        x = Dense(128, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.1)(x)
        # and a logistic layer -- let's say we have 200 classes
        predictions = Dense(2, activation='softmax')(x)
        # this is the model we will train
        model = Model(inputs=base_model.input, outputs=predictions)

def upload_path(instance, filename):
    return '/'.join(['covid_images', filename])


class Image(models.Model):
    name = models.CharField(max_length=32, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=upload_path)
    prediction = models.CharField(max_length = 12, blank=True)
    time = models.DateTimeField(default = timezone.now)


    def pred(self):
        fileObj =self.image
        fs = FileSystemStorage()
        filePathName = fs.save(fileObj.name, fileObj)
        filePathName = fs.url(filePathName)
        test_image='.'+filePathName

        img = cv2.imread(test_image, cv2.IMREAD_COLOR)       #cv2.IMREAD_GRAYSCALE
        img = cv2.resize(img, (ROWS, COLS), interpolation=cv2.INTER_CUBIC)
        image = tf.reshape(img,(-1, ROWS, COLS,3))
        with model_graph.as_default():
            with tf_session.as_default():
                preds = model.predict(image, steps=1) # Predict image

        pred_label = preds
        return pred_label

    def save(self, *args, **kwargs):
        if not self.prediction:
            self.prediction= self.pred()
        super(Image, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
