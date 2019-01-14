import os
import sys
import uuid
import subprocess
from pydub import AudioSegment
import json
from flask import Flask, request, render_template, url_for, jsonify

from google_apis import text_to_speech, transcribe_speech, translate_text

lib_dir = os.path.join(os.getcwd(), "./tensorflow")
sys.path.append(lib_dir)

from predict import predict


def prolong_audio(fname, expected_duration):
    # if the audio file is shorter than it should be, a necessary amount of silence is added
    f = AudioSegment.from_wav(fname)
    f_duration = f.duration_seconds
    if f_duration > expected_duration:
        return
    silence_duration = (expected_duration - f_duration) * 1000 #the method on the line below uses miliseconds
    silence = AudioSegment.silent(duration=silence_duration)
    final = f + silence
    final.export(fname, format="wav")


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        # writing the recorded audio
        filename = 'static/tmp/recording_{0}.wav'.format(uuid.uuid4())
        f = open(filename, 'wb')
        f.write(request.data)
        f.close()

        # adding silence if the audio file is not long enough
        prolong_audio(filename, 3)

        # detecting the language in audio 
        detected_lang, probabilities = predict(filename)
        probabilities = ' '.join(str(format(elem, '.4f')) for elem in probabilities)

        flag = 'static/images/{}.png'.format(detected_lang)
        
        return jsonify(flag=flag, detected_lang=detected_lang, probabilities=probabilities, filename=filename)
    
    return render_template('index.html')


@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    filename = request.args.get('filename')
    detected_lang = request.args.get('detected_lang')
    transcription = transcribe_speech(filename, detected_lang)
    os.remove(filename)
    return jsonify(transcription=transcription)


@app.route('/get_translation', methods=['GET'])
def get_translation():
    transcription = request.args.get('transcription')
    translation = translate_text(transcription)
    return jsonify(translation=translation)


@app.route('/get_output_speech', methods=['GET'])
def get_output_speech():
    translation = request.args.get('translation')
    # text-to-speech of the translated text
    output_speech = text_to_speech(translation, 'static/tmp/output_{0}.mp3'.format(uuid.uuid4()))
    return jsonify(output_speech=output_speech)


if __name__ == "__main__":
    app.run(debug=False, threaded=True) 