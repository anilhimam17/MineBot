import gradio as gr
import pyttsx3
import speech_recognition as sr
from minecraft_assistant.agents.llm_agent import LLMAgent


# Variables to construct the agent
AGENT_NAME = "deepseek-chat"
IS_LOCAL = False


class GradioInterface:
    """Class to abstract all the gradio orchestration."""
    def __init__(self) -> None:
        self.gradio_block = gr.Blocks()
        self.llm_agent = LLMAgent(AGENT_NAME, IS_LOCAL)
        self.recognizer = sr.Recognizer()
        # self.tts_engine = pyttsx3.init()

        # Configure recognizer settings for better performance
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

        audio_file = "output_audio.mp3"
        _ = engine.save_to_file(text, audio_file)
        _ = engine.runAndWait()
        _ = engine.stop()
        return audio_file

    def process_input(self, input_text: str, audio_input: str | None):
        """Process either text or audio input and return the LLM response and speech output."""

        if audio_input:
            transcribed_text = self.transcribe_audio(audio_input)
            if transcribed_text:
                response = self.llm_agent.run_pipeline(transcribed_text)
                return response, self.generate_speech(response)
            print("Sorry, I couldn't understand the audio input.")
            return None, None

        response = self.llm_agent.run_pipeline(input_text)
        return response, self.generate_speech(response)

    def run(self) -> None:
        """Build and run the Gradio interface with enhanced ASR and TTS capabilities."""
        with self.gradio_block:
            _ = gr.Markdown("<h1 style='text-align: center'>Minecraft Assistant</h1>")

            with gr.Row():
                with gr.Column():
                    chatbot_ui = gr.Chatbot(height=500)

                    with gr.Row():
                        message_box = gr.Textbox(
                            placeholder="Type your Minecraft question or command...",
                            label="Text Input", scale=4
                        )
                        mic_input = gr.Audio(
                            sources=["microphone"], type="filepath", label="Voice Input",
                            show_label=True, scale=1
                        )

                    submit_btn = gr.Button("Submit", variant="primary")
                    tts_output = gr.Audio(label="Assistant Speech Output", type="filepath", autoplay=True, interactive=False)

                    _ = submit_btn.click(
                        self.process_input, inputs=[message_box, mic_input], outputs=[chatbot_ui, tts_output]
                    )

                    _ = submit_btn.click(
                        lambda: ("", None), outputs=[message_box, mic_input]
                    )

        _ = self.gradio_block.launch(debug=True)

    # def run(self) -> None:
    #     """Build and run the gradio interface on localhost."""

    #     with self.gradio_block:
    #         _ = gr.Markdown(
    #             "<h1 style={text-align: center}>Minecraft Assistant</h1>"
    #         )

    #         chatbot_ui = gr.Chatbot()
    #         message_box = gr.Textbox("Let's cookup some minecraft")

    #         # Voice interface declaration
    #         # mic = gr.Audio(
    #         #     sources=["microphone"], type="filepath", label="Wanna, start a Chat ?"
    #         # )

    #         # # Microphone pipeline
    #         # mic.change(process_audio, inputs=mic, outputs=chatbot_ui)

    #         # Compiling the entire pipeline for the input / output
    #         _ = message_box.submit(
    #             self.llm_agent.run_pipeline, inputs=[message_box], outputs=[chatbot_ui]
    #         )

    #     _ = self.gradio_block.launch(debug=True)
