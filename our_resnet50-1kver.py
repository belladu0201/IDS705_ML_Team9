"""Resnet model for classification of real and fake images."""

import os

import matplotlib.pyplot as plt

import numpy as np
import glob
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
import time
from PIL import Image

script_time = time.time()

# Apparently for monitoring, it only shows in terminals
tflow.debugging.set_log_device_placement(True)

# Set up Prefetching
AUTOTUNE = tflow.data.AUTOTUNE

# Image opening test

IMAGE_SIZE = (256, 256)  # height, width

batch_size = 32  # 32 is default recommendation for vision models

# calculate length  of elements in One1ksetDraft
n_samples = 0
for each_folder in os.listdir("One1ksetDraft"):
    print("Folder: {}".format(each_folder))
    print(
        "Number of images: {}".format(
            len(os.listdir("One1ksetDraft/{}".format(each_folder)))
        )
    )
    n_samples += len(os.listdir("One1ksetDraft/{}".format(each_folder)))


# the ratio for the splits
train_ratio = 0.7
val_ratio = 0.3

# adjustment for tensorflow 2.0

train_ds = tflow.keras.preprocessing.image_dataset_from_directory(
    "One1ksetDraft",
    label_mode="binary",
    validation_split=val_ratio,
    shuffle=True,
    subset="training",
    seed=417,
    image_size=IMAGE_SIZE,
    batch_size=batch_size,
)

validation_ds = tflow.keras.preprocessing.image_dataset_from_directory(
    "One1ksetDraft",
    validation_split=val_ratio,
    shuffle=True,
    subset="validation",
    seed=417,
    label_mode="binary",
    image_size=IMAGE_SIZE,
    batch_size=batch_size,
)
# for the test split
val_batches = tflow.data.experimental.cardinality(validation_ds)
test_ds = validation_ds.take((2 * val_batches) // 3)
val_ds = validation_ds.skip((2 * val_batches) // 3)

print("Num GPUs Available: ", len(tflow.config.list_physical_devices("GPU")))
print(tflow.config.list_physical_devices("GPU"))
print("Num CPUs Available: ", len(tflow.config.list_physical_devices("CPU")))
print(tflow.config.list_physical_devices("CPU"))


with tflow.device("/GPU:0"):
    gpu_time = time.time()
    # Test for gpu code
    # Create some tensors
    a = tflow.constant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    b = tflow.constant([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    c = tflow.matmul(a, b)
    gpu_time = time.time() - gpu_time
    print("GPU time for basic tensor operation: {} seconds".format(gpu_time))

with tflow.device("/CPU:0"):
    cpu_time = time.time()
    # Test for cpu code
    # Create some tensors
    a = tflow.constant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    b = tflow.constant([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    c = tflow.matmul(a, b)
    cpu_time = time.time() - cpu_time
    print("CPU time for basic tensor operation: {} seconds".format(cpu_time))


# Visualize six random images from combined list

# import matplotlib.pyplot as plotter_lib

# plotter_lib.figure(figsize=(10, 10))

epochs = 10

# for images, labels in train_ds.take(1):
#     for var in range(6):
#         ax = plt.subplot(3, 3, var + 1)

#         plotter_lib.imshow(images[var].numpy().astype("uint8"))

#         plotter_lib.axis("off")


# Model creation

demo_resnet_model = Sequential()
IMAGE_SIZE_INT = 256
IMAGE_SIZE = (256, 256)  # height, width
pretrained_model_for_demo = tflow.keras.applications.ResNet50(
    include_top=False,
    input_shape=(IMAGE_SIZE_INT, IMAGE_SIZE_INT, 3),
    pooling="avg",
    weights="imagenet",
)

for each_layer in pretrained_model_for_demo.layers:
    each_layer.trainable = False

demo_resnet_model.add(pretrained_model_for_demo)


demo_resnet_model.add(Flatten())

demo_resnet_model.add(Dense(512, activation="relu"))

demo_resnet_model.add(Dense(1, activation="sigmoid"))

demo_resnet_model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss="binary_crossentropy",
    metrics=[
        "accuracy",
        "AUC",
        "Precision",
        "Recall",
        "TruePositives",
        "TrueNegatives",
        "FalsePositives",
        "FalseNegatives",
    ],
)

history = demo_resnet_model.fit(
    train_ds,
    validation_data=validation_ds,
    epochs=epochs,
    verbose=1,
    # callbacks=[tflow.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)],
)

# # Visualize the training and validation accuracy and loss

# plotter_lib.figure(figsize=(10, 10))

# plotter_lib.subplot(2, 1, 1)

# plotter_lib.plot(history.history["accuracy"], label="Training Accuracy")

# plotter_lib.plot(history.history["val_accuracy"], label="Validation Accuracy")

# plotter_lib.legend(loc="lower right")

# plotter_lib.ylabel("Accuracy")

# plotter_lib.title("Training and Validation Accuracy")

# plotter_lib.subplot(2, 1, 2)

# plotter_lib.plot(history.history["loss"], label="Training Loss")

# plotter_lib.plot(history.history["val_loss"], label="Validation Loss")

# plotter_lib.legend(loc="upper right")

# plotter_lib.ylabel("Cross Entropy")

# plotter_lib.title("Training and Validation Loss")

# plotter_lib.xlabel("epoch")

# plotter_lib.show()


# Save the model

# demo_resnet_model.save("demo_resnet_model.h5")

# demo_resnet_model.save_weights("demo_resnet_model_weights.h5")

# predicting on the training set
prediction_time = time.time()
# train_predictions = demo_resnet_model.predict(train_ds)
test_ds_pred = demo_resnet_model.predict(test_ds)
prediction_time = time.time() - prediction_time
print("Prediction time for test set: {} seconds".format(prediction_time))
evaluation = demo_resnet_model.evaluate(test_ds, verbose=1, return_dict=True)

# processing the predictions
imgs_arr = []
labels_arr = []

for img, label in test_ds.take(-1):
    print(img.dtype)
    imgs_arr.append(img.numpy(d))
    labels_arr.append(label.numpy())

imgs_ls = [img for batch in imgs_arr for img in batch]
labels_ls = np.array([label for batch in labels_arr for label in batch])

# Example of image reconstruction
# Image.fromarray((imgs_ls[0] * 255).astype(np.uint8)).convert("RGB")
# solution
# Image.fromarray((imgs_ls[0] * 1).astype(np.uint8)).convert("RGB")

# roc curve for models
from sklearn.metrics import roc_curve

fpr, tpr, thresh = roc_curve(labels_ls, test_ds_pred)
# plot roc curve
plotter_lib.plot(fpr, tpr, linestyle="--", color="orange", label="ResNet50")
# axis labels
plotter_lib.xlabel("False Positive Rate")
plotter_lib.ylabel("True Positive rate")
plotter_lib.legend(loc="best")
plotter_lib.title("ROC curve")
plotter_lib.show()


# from sklearn.metrics import classification_report
# classification_report(labels_ls, test_ds_pred.round())


# Load the model

# demo_resnet_model_saved = tflow.keras.models.load_model("demo_resnet_model.h5")

# Predict on a single image

# single_image_prediction_time = time.time()

# img = Image.open("Data/combined_subset/F0.png")

# img = img.resize((128, 128))

# img = np.expand_dims(img, axis=0)

# img = np.array(img)

# img = img / 255.0

# prediction = demo_resnet_model.predict(img)

# single_image_prediction_time = time.time() - single_image_prediction_time

# print(prediction)

# print(
#     "Prediction time for single image: {} seconds".format(single_image_prediction_time)
# )


# Predict on a batch of images

# batch_of_images = []
# batch_prediction_time = time.time()
# for filename in glob.glob("Data/combined_subset/*.png"):  # assuming png
#     im = Image.open(filename)

#     im = im.resize((128, 128))

#     im = np.expand_dims(im, axis=0)

#     im = np.array(im)

#     im = im / 255.0

#     batch_of_images.append(im)

# batch_of_images = np.array(batch_of_images)

# batch_of_images = np.reshape(batch_of_images, (200, 128, 128, 3))

# predictions = demo_resnet_model.predict(batch_of_images)
# batch_prediction_time = time.time() - batch_prediction_time
# # print(predictions)
# print("Prediction time for batch of images: {} seconds".format(batch_prediction_time))

### From reference

# plotter_lib.figure(figsize=(8, 8))

# epochs_range = range(epochs)

# plotter_lib.plot(epochs_range, history.history["accuracy"], label="Training Accuracy")

# plotter_lib.plot(
#     epochs_range, history.history["val_accuracy"], label="Validation Accuracy"
# )

# plotter_lib.axis(ymin=0.4, ymax=1)

# plotter_lib.grid()

# plotter_lib.title("Model Accuracy")

# plotter_lib.ylabel("Accuracy")

# plotter_lib.xlabel("Epochs")

# plotter_lib.legend(["train", "validation"])

# plotter_lib.show()

# plotter_lib.savefig("output-plot.png")

script_time = time.time() - script_time
print("Total GPU script time: {} seconds".format(script_time))
print("We did it, everybody. See you next time!")
print("The full train, val and test run has completed")
print("Test Metrics for the ResNet50 model")
print(f"Test metrics : {evaluation}")
print("Kashaf, Bella, Eric, and mean old Tensorflow : GPU Version")
# write the results to a file
with open("output.txt", "w") as f:
    f.write("Total GPU script time: {} seconds".format(script_time))
    f.write("The full train, val and test run has completed")
    f.write("Test Metrics for the ResNet50 model")
    f.write(f"Test metrics : {evaluation}")
