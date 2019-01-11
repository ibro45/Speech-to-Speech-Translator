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




app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    global data
    data = {'filename': "", 'flag': "", 'transcribed': "", 'translated': "", 'output_speech':"", 'detected_lang': "", 'probabilities': ""}

    if request.method == 'POST':
        data['filename'] = 'static/tmp/recording_{0}.wav'.format(uuid.uuid4())
        downsampled = 'static/tmp/downsampled_{0}.wav'.format(uuid.uuid4())

        f = open(data['filename'], 'wb')
        f.write(request.data)
        f.close()

        prolong_audio(data['filename'], 3)

        command = ["ffmpeg", "-i", data['filename'], "-map", "0", "-ac", "1", "-ar", "16000", downsampled]
        subprocess.call(command)
        
        # audio normalisation
        neg23File(downsampled)

        # detecting the language in audio 
        try:
            data['detected_lang'], data['probabilities'] = predict(downsampled)
            data['probabilities'] = ' '.join(str(format(elem, '.4f')) for elem in data['probabilities'])
        except Exception as e:
            print( 'Error occured:\n{}'.format(e) )

        os.remove(downsampled)

        data['flag'] = 'static/images/{}.png'.format(data['detected_lang'])
 
    return render_template('index.html')


@app.route('/get_flag_and_probs', methods=['GET'])
def get_flag_image():
    return jsonify(flag=data['flag'], probabilities=data['probabilities'])


@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    # transcribes what's said in the audio. Does it better when the audio's not downsampled.
    data['transcribed'] = transcribe_speech(data['filename'], data['detected_lang'])
    os.remove(data['filename'])
    return jsonify(transcription=data['transcribed'])


@app.route('/get_translation', methods=['GET'])
def get_translation():
    data['translated'] = translate_text(data['transcribed'])
    return jsonify(translation=data['translated'])


@app.route('/get_output_speech', methods=['GET'])
def get_output_speech():
    # text-to-speech of the translated text
    data['output_speech'] = text_to_speech(data['translated'])
    return jsonify(output_speech=data['output_speech'])


if __name__ == "__main__":
    app.run(debug=False, threaded=True) 