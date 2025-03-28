import os

from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment


''' To download:
1.  On macOS: brew install ffmpeg
    On Linux: sudo apt install ffmpe
2. pip install gTTS pydub speechrecognition gradio
'''


class AutomaticSpeechRecognition:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def transcribe_audio(self, audio_file: str) -> str | None:
        try:
            with sr.AudioFile(audio_file) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
                try:
                    return self.recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Error processing audio: {e}")
        return None

    def generate_speech(self, text: str) -> str | None:
        try:
            if isinstance(text, list):
                text = " ".join(str(item) for item in text)
            text = str(text).strip()

            raw_filename = f"./audio/temp_audio_{os.urandom(4).hex()}.mp3"
            tts = gTTS(text=text, lang='en')
            tts.save(raw_filename)

            # Step 2: Load and slightly increase speed (e.g. 1.1x)
            audio = AudioSegment.from_file(raw_filename)
            faster_audio = audio._spawn(
                audio.raw_data,
                overrides={
                    "frame_rate": int(audio.frame_rate * 1.1)
                    }
                ).set_frame_rate(audio.frame_rate)

            # Step 3: Save sped-up version
            final_filename = f"output_audio_{os.urandom(4).hex()}.mp3"
            faster_audio.export(final_filename, format="mp3")

            # Optional cleanup
            os.remove(raw_filename)

            print(f"Speech generated and saved to {final_filename}")
            return final_filename
        except Exception as e:
            print(f"TTS error: {e}")
            return None
