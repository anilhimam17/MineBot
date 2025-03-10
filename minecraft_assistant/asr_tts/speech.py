import os
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# I recommend to run this script using a virtual environment.
# To set up and activate a virtual environment:
# python3 -m venv venv
# source venv/bin/activate  (On macOS/Linux)
# venv\Scripts\activate      (On Windows)

# Required dependencies:
# Install the necessary packages through terminal or etc:
# pip install azure-cognitiveservices-speech python-dotenv
# pip install flask

# Load environment variables
load_dotenv()

SPEECH_KEY = os.getenv("speech_key")
SPEECH_REGION = os.getenv("speech_region")

if not SPEECH_KEY or not SPEECH_REGION:
    raise ValueError("Azure Speech Key or Region not set in .env file.")

app = Flask(__name__)

### ASR (Speech-to-Text) ###
def recognize_speech():
    """Converts speech to text using Azure Speech SDK."""
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("Listening for speech...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return {"recognized_text": result.text}
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return {"error": "No speech recognized."}
    elif result.reason == speechsdk.ResultReason.Canceled:
        return {"error": f"Speech recognition canceled: {result.cancellation_details}"}

### TTS (Text-to-Speech) ###
def text_to_speech(text):
    """Converts text to speech using Azure Speech SDK."""
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return {"message": "Speech synthesis successful"}
    elif result.reason == speechsdk.ResultReason.Canceled:
        return {"error": f"Speech synthesis canceled: {result.cancellation_details}"}

### Flask Endpoints ###

@app.route('/asr', methods=['POST'])
def asr():
    """API Endpoint to recognize speech from user."""
    result = recognize_speech()
    return jsonify(result)

@app.route('/tts', methods=['POST'])
def tts():
    """API Endpoint to convert text to speech."""
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    response = text_to_speech(text)
    return jsonify(response)

@app.route('/status', methods=['GET'])
def status():
    """Check if ASR and TTS are running."""
    return jsonify({"status": "Speech API is running!"})

if __name__ == '__main__':
    # example port, had to be chaged to follow deepseeks port.
    app.run(host='0.0.0.0', port=5000)
