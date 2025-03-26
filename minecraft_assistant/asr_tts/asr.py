import pyttsx3
import speech_recognition as sr


class AutomaticSpeechRecognition:
    """Class that implements all the utilities and functions requried for ASR."""
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()

        # Configuration for the speech recognizer for better performance
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def transcribe_audio(self, audio_file: str) -> str | None:
        """Implements the speech to the text conversion with error handling."""

        try:
            with sr.AudioFile(audio_file) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)

                try:
                    text = self.recognizer.recognize_google(audio_data)
                    return text
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                    return None
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    return None
        except Exception as e:
            print(f"Error processing audio file: {e}")
            return None

    def generate_speech(self, text: str) -> str:
        """Implenets the text to speech (NLG) and saves the audio file"""

        engine = pyttsx3.init()

        # Configure TTS engine settings
        _ = engine.setProperty('rate', 150)  # Adjust speech rate
        _ = engine.setProperty('volume', 1.0)  # Adjust volume

        audio_file = "output_audio.wav"
        _ = engine.save_to_file(text, audio_file)
        _ = engine.runAndWait()
        _ = engine.stop()
        return audio_file
