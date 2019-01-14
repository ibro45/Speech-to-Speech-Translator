import os
import sys
import time

import numpy as np
import tensorflow
import tensorflow.keras
from tensorflow.keras.models import load_model
from yaml import load

# local modules
from SpectrogramGenerator import SpectrogramGenerator
from compile_model import compile_model

tensorflow.keras.backend.clear_session()

# change the path to weights accordingly
model_dir = 'tensorflow/trained_model/weights.07.model'
print("Loading model: {}".format(model_dir))
model = load_model(model_dir)
model = compile_model(model)

# https://github.com/keras-team/keras/issues/6462#issuecomment-385962748
global graph
graph = tensorflow.get_default_graph()


def predict(input_file):

    config = load(open('tensorflow/config.yaml', "rb"))
    class_labels = config["label_names"]
    
    params = {"pixel_per_second": config["pixel_per_second"], "input_shape": config["input_shape"], "num_classes": config["num_classes"]}
    data_generator = SpectrogramGenerator(input_file, params, shuffle=False, run_only_once=True).get_generator()
    data = [np.divide(image, 255.0) for image in data_generator]
    data = np.stack(data)

    # Model Generation
    with graph.as_default():
        probabilities = model.predict(data)

    classes = np.argmax(probabilities, axis=1)
    average_prob = np.mean(probabilities, axis=0)
    average_class = np.argmax(average_prob)

    print(classes, class_labels[average_class], average_prob)
    return class_labels[average_class], average_prob