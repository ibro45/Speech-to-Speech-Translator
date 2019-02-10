# The Babel Fish - Speech-to-Speech Translator

  
  This speech-to-speech translator is inspired by the infamous *Hitchhiker's Guide to Galaxy* and its Babel fish.
>The Babel fish is a small, bright yellow fish, which can be placed in someone's ear in order for them to be able to hear any language translated into their first language. ([source](https://hitchhikers.fandom.com/wiki/Babel_Fish))

Here's a short, 1-minute, excerpt from the movie based on the mentioned novel, featuring the Babel fish:
[![The Babel Fish | YouTube](https://img.youtube.com/vi/YWqHkYtREAE/0.jpg)](https://www.youtube.com/watch?v=YWqHkYtREAE)
  

This translator, named *The Babel Fish v0.01* achieves something that reminds of it by using a neural network to identify the language that a speaker is talking. 
Once it has recognised the language, that information is passed on to several Google APIs in order to produce the English translation of it and to return it as synthesised speech.
	
It currently supports Croatian, French and Spanish and the default output language is English.

Here you can see the video of the application in action

[![The Babel Fish v0.01| YouTube](https://img.youtube.com/vi/RN3c_3j5m4U/0.jpg)](https://www.youtube.com/watch?v=RN3c_3j5m4U)

## Technical details

The neural network was created and trained using Tensorflow and the code for it can be found in the following repository: [Language-Identification-Speech](https://github.com/ibro45/Language-Identification-Speech)

The project's backend is written in `flask`. 
The Google APIs are used for:

 - Speech recognition ([Speech-to-Text](https://cloud.google.com/speech-to-text/docs/))
 - Text translation ([Translate](https://cloud.google.com/translate/docs/))
 - Speech synthesis ([Text-to-Speech](https://cloud.google.com/text-to-speech/docs/)).

## Requirements
To install the dependencies, run

    pip install -r requirements.txt 

You should also have the following utilities installed in your system:

 - FFmpeg
 - SoX

## Running it up
Before running `$ flask run` in the root folder of the project, make sure to specify the path to the trained model in the `tensorflow/predict.py`. 
After running the local server, you'll be able to access the app at the `http://127.0.0.1:5000` .

## List of scripts
|Name|Description|
|--|--|
| [**app.py**](https://github.com/ibro45/Speech-to-Speech-Translator/blob/master/app.py) | Backend. Runs the server. Defines the routes and the functionality depending on the requests made.|
|[**google_apis.py**](https://github.com/ibro45/Speech-to-Speech-Translator/blob/master/google_apis.py)| Contains methods for the above mentioned Google APIs.|
| [**tensorflow/SpectrogramGenerator.py**](https://github.com/ibro45/Speech-to-Speech-Translator/blob/master/tensorflow/SpectrogramGenerator.py) |  Given an audio input, the generator segments it into 3 seconds and creates spectrograms out of them. The spectrograms are what the neural network takes as input.|
| [**tensorflow/compile_model.py**](https://github.com/ibro45/Speech-to-Speech-Translator/blob/master/tensorflow/compile_model.py) |  Compiles the `tensorflow.keras` model with specified parameters. Present because a trained model may not have been compiled if it were trained using multiple GPUs due to the way in which the model is saved.|
| [**tensorflow/config.yaml**](https://github.com/ibro45/Speech-to-Speech-Translator/blob/master/tensorflow/config.yaml) |  Defines several important and self-explanatory parameters and values.|
| [**tensorflow/predict.py**](https://github.com/ibro45/Speech-to-Speech-Translator/blob/master/tensorflow/predict.py) |  Uses the trained model to predict the language spoken in a recording.|
| [**static/js/app.js**](https://github.com/ibro45/Speech-to-Speech-Translator/blob/master/static/js/app.js) |  Allows the website to record by using [Recorder.js](https://github.com/mattdiamond/Recorderjs). Sends the recording to the backend. Receives and displays the results from the backend.|
