import io
import os
import html
import uuid
from google.cloud import texttospeech
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import translate

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./gcloud_account.json"

lang_codes = {'croatian': 'hr-HR',
              'french'  : 'fr-FR',
              'spanish' : 'es-ES'}

def transcribe_speech(speech_file, detected_lang): 
    language_code = lang_codes[detected_lang]
    # Transcribe the given audio file
    client = speech.SpeechClient()

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code=language_code) 

    response = client.recognize(config, audio)
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    transcribed = ""
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))
        transcribed += result.alternatives[0].transcript

    print('Final transcript: {}'.format(transcribed))
    
    return transcribed


def translate_text(text, target_language='en'):
    # Instantiates a client
    translate_client = translate.Client()
    # Translates some text into Russian
    translation = translate_client.translate(
        text,
        target_language=target_language)
    print(u'Translation: {}'.format(translation['translatedText']))
    return html.unescape(translation['translatedText'])


def text_to_speech(text, filename='output.mp3', language_code='en-GB'):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    with open(filename, 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "{0}"'.format(filename))

    return filename
