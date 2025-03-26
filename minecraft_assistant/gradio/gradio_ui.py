import gradio as gr

from minecraft_assistant.agents.llm_agent import LLMAgent
from minecraft_assistant.asr_tts.asr import AutomaticSpeechRecognition


# Variables to construct the agent
AGENT_NAME = "deepseek-chat"
IS_LOCAL = False


class GradioInterface:
    """Class to abstract all the gradio orchestration."""
    def __init__(self) -> None:
        self.gradio_block = gr.Blocks()
        self.llm_agent = LLMAgent(AGENT_NAME, IS_LOCAL)
        self.asr = AutomaticSpeechRecognition()

    def process_input(self, input_text: str, audio_input: str | None):
        """Process either text or audio input and return the LLM response and speech output."""

        if audio_input:
            transcribed_text = self.asr.transcribe_audio(audio_input)
            if transcribed_text:
                response = self.llm_agent.run_pipeline(transcribed_text)
                return response, self.asr.generate_speech(response)
            print("Sorry, I couldn't understand the audio input.")
            return None, None

        response = self.llm_agent.run_pipeline(input_text)
        return response, self.asr.generate_speech(response)

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
