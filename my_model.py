"""Resnet model for classification of real and fake images."""

import os

import matplotlib.pyplot as plt

import numpy as np

import PIL as image_lib

import tensorflow as tflow

from tensorflow.keras.layers import Flatten

from keras.layers.core import Dense

from tensorflow.keras.models import Sequential

from tensorflow.keras.optimizers import Adam

from PIL import Image

import matplotlib.pyplot as plotter_lib

import numpy as np

import PIL as image_lib

import tensorflow as tflow

from tensorflow.keras.layers import Flatten

from keras.layers.core import Dense

from tensorflow.keras.models import Sequential

from tensorflow.keras.optimizers import Adam

real_data_directory = "Data/Real"
fake_data_directory = "Data/Fake"

img = Image.open(r"Data\Real\00998.png")

# img.show(), shows the image in viewer

# img.size, returns the size of the image

# img.format, returns the format of the image

# img.mode, returns the mode of the image (RGB)

real_images = []
real_images_labels = []

fake_images = []
fake_images_labels = []

# for i in range(1, len(os.listdir(real_data_directory)) + 1):

#         real_images.append(Image.open((real_data_directory + '/' + str(i) + '.png')))

#         fake_images.append((fake_data_directory + '/' + str(i) + '.png'))

from PIL import Image
import glob

for filename in glob.glob("Data/Real/*.png"):  # assuming png
    im = Image.open(filename)
    real_images.append(im)
    real_images_labels.append(1)


for filename in glob.glob("Data/Fake/*.jpg"):  # assuming jpg
    im = Image.open(filename)
    filename = filename.replace("Fake", "Fakepng")
    im.save((filename[:-3] + "png"))

for filename in glob.glob("Fakepng/*.png"):  # assuming png
    fake_images.append(im)
    fake_images_labels.append(0)

combined_images = real_images + fake_images
combined_labels = real_images_labels + fake_images_labels

# last combine
final_combined_labels = []


fake_counter = 0
for filename in glob.glob("Data/Fakepng/*.png"):  # assuming png
    im = Image.open(filename)
    new_filename = "Data/combined_subset/" + "F" + str(fake_counter) + ".png"
    im.save(new_filename)
    final_combined_labels.append(0)
    fake_counter += 1

real_counter = 0
for filename in glob.glob("Data/Real/*.png"):  # assuming png
    im = Image.open(filename)
    new_filename = "Data/combined_subset/" + "R" + str(real_counter) + ".png"
    im.save(new_filename)
    final_combined_labels.append(1)
    real_counter += 1
    if real_counter == 100:
        break


IMAGE_SIZE = [224, 224]

batch_size = 32

final_combined_labels_array = np.array(final_combined_labels)

train_ds = tflow.keras.preprocessing.image_dataset_from_directory(
    "Data/combined_subset/",
    labels=final_combined_labels,
    label_mode="int",
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMAGE_SIZE,
    batch_size=batch_size,
)


validation_ds = tflow.keras.preprocessing.image_dataset_from_directory(
    "Data/combined_subset/",
    validation_split=0.2,
    subset="validation",
    seed=123,
    labels=final_combined_labels,
    label_mode="int",
    image_size=IMAGE_SIZE,
    batch_size=batch_size,
)


# Visualize six random images from combined list

zipped_images = tuple(zip(combined_images, combined_labels))

import matplotlib.pyplot as plotter_lib

plotter_lib.figure(figsize=(10, 10))

epochs = 10

for images, labels in train_ds.take(1):
    for var in range(6):
        ax = plt.subplot(3, 3, var + 1)

        plotter_lib.imshow(images[var].numpy().astype("uint8"))

        plotter_lib.axis("off")


demo_resnet_model = Sequential()

pretrained_model_for_demo = tflow.keras.applications.ResNet50(
    include_top=False,
    input_shape=(224, 224, 3),
    pooling="avg",
    classes=5,
    weights="imagenet",
)

for each_layer in pretrained_model_for_demo.layers:
    each_layer.trainable = False

demo_resnet_model.add(pretrained_model_for_demo)


demo_resnet_model.add(Flatten())

demo_resnet_model.add(Dense(512, activation="relu"))

demo_resnet_model.add(Dense(1, activation="sigmoid"))

demo_resnet_model.compile(
    optimizer=Adam(lr=0.001), loss="binary_crossentropy", metrics=["accuracy"]
)

history = demo_resnet_model.fit(train_ds, validation_data=validation_ds, epochs=epochs)
