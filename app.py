import os
import sys
import uuid
import subprocess
from pydub import AudioSegment
import json
from flask import Flask, request, render_template, url_for, jsonify

lib_dir = os.path.join(os.getcwd(), "./tensorflow")
sys.path.append(lib_dir)

from normalise import neg23File
from predict import predict#, predict2
from google_apis import text_to_speech, transcribe_speech, translate_text

def prolong_audio(fname, expected_duration):
    # if the audio file is shorter than it should be, 
    # a sufficient amount of silence is added
    f = AudioSegment.from_wav(fname)
    f_duration = f.duration_seconds
    if f_duration > expected_duration:
        return
    silence_duration = (expected_duration - f_duration) * 1000
    silence = AudioSegment.silent(duration=silence_duration)
    final = f + silence
    final.export(fname, format="wav")

class appData:

    def __init__(self):
        self.filename = ""
        self.flag = ""
        self.transcribed = ""
        self.translated = ""
        self.output_speech = ""
        self.detected_lang = ""
        self.probabilities = ""

app_data = appData()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        app_data.filename = 'static/tmp/recording_{0}.wav'.format(uuid.uuid4())
        app_data.downsampled = 'static/tmp/downsampled_{0}.wav'.format(uuid.uuid4())

        f = open(app_data.filename, 'wb')
        f.write(request.data)
        f.close()

        prolong_audio(app_data.filename, 3)

        command = ["ffmpeg", "-i", app_data.filename, "-map", "0", "-ac", "1", "-ar", "16000", app_data.downsampled]
        subprocess.call(command)
        
        # audio normalisation
        neg23File(app_data.downsampled)

        # detecting the language in audio 
        try:
            app_data.detected_lang, app_data.probabilities = predict(app_data.downsampled)
            app_data.probabilities = ' '.join(str(format(elem, '.4f')) for elem in app_data.probabilities)
        except Exception as e:
            print( 'Error occured:\n{}'.format(e) )

        os.remove(app_data.downsampled)

        app_data.flag = 'static/images/{}.png'.format(app_data.detected_lang)
 
    return render_template('index.html')


@app.route('/get_flag_and_probs', methods=['GET'])
def get_flag_image():
    return jsonify(flag=app_data.flag, probabilities=app_data.probabilities)


@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    # transcribes what's said in the audio. Does it better when the audio's not downsampled.
    app_data.transcribed = transcribe_speech(app_data.filename, app_data.detected_lang)
    os.remove(app_data.filename)
    return jsonify(transcription=app_data.transcribed)


@app.route('/get_translation', methods=['GET'])
def get_translation():
    app_data.translated = translate_text(app_data.transcribed)
    return jsonify(translation=app_data.translated)


@app.route('/get_output_speech', methods=['GET'])
def get_output_speech():
    # text-to-speech of the translated text
    app_data.output_speech = text_to_speech(app_data.translated)
    return jsonify(output_speech=app_data.output_speech)


if __name__ == "__main__":
    app.run(debug=False) 
