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
from predict import predict
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


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':

        filename = 'static/tmp/recording_{0}.wav'.format(uuid.uuid4())
        downsampled = 'static/tmp/downsampled_{0}.wav'.format(uuid.uuid4())

        f = open(filename, 'wb')
        f.write(request.data)
        f.close()

        prolong_audio(filename, 3)

        command = ["ffmpeg", "-i", filename, "-map", "0", "-ac", "1", "-ar", "16000", downsampled]
        subprocess.call(command)
        
        # audio normalisation
        neg23File(downsampled)

        # detecting the language in audio 
        try:
            detected_lang, probabilities = predict(downsampled)
            probabilities = ' '.join(str(format(elem, '.4f')) for elem in probabilities)
        except Exception as e:
            print( 'Error occured:\n{}'.format(e) )

        os.remove(downsampled)

        flag = 'static/images/{}.png'.format(detected_lang)
        
        return jsonify(flag=flag, detected_lang=detected_lang, probabilities=probabilities, filename=filename)
    
    return render_template('index.html')


@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    filename = request.args.get('filename')
    detected_lang = request.args.get('detected_lang')
    # transcribes what's said in the audio. Does it better when the audio's not downsampled.
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
    output_speech = text_to_speech(translation)
    return jsonify(output_speech=output_speech)


if __name__ == "__main__":
    app.run(debug=False, threaded=True) 