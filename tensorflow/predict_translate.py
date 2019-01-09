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
from google_apis import transcribe_speech, translate_text, speech_to_text

tensorflow.keras.backend.clear_session()
model_dir = 'tensorflow/trained_model/inception_resnet_v2.weights.21.model' #  inceptionv3.weights.18.model
print("Loading model: {}".format(model_dir))
model = load_model(model_dir)

# https://github.com/keras-team/keras/issues/6462
global graph
graph = tensorflow.get_default_graph()

lang_codes = {'croatian': 'hr-HR',
              'french'  : 'fr-FR',
              'spanish' : 'es-ES'}

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
    return class_labels[average_class]


def predict_translate(wav_file):
    result = predict(wav_file)
    print(result)

    transcribed = transcribe_speech(wav_file, lang_codes[result])
    translated = translate_text(transcribed)
    output_speech = speech_to_text(translated)

    return result, output_speech

