import gradio as gr


class GradioInterface:
    """Class to abstract all the gradio orchestration."""
    def __init__(self) -> None:
        self.gradio_block = gr.Blocks()

    def run(self) -> None:
        """Build and run the gradio interface on localhost."""

        with self.gradio_block:
            _ = gr.Markdown(
                "<h1 style={text-align: center}>Minecraft Assistant</h1>"
            )

            chatbot_ui = gr.Chatbot()
            message_box = gr.Textbox("Let's cookup some minecraft")
            state = gr.State()

            # Voice interface declaration
            mic = gr.Audio(
                sources=["microphone"], type="filepath", label="Wanna, start a Chat ?"
            )

            # Microphone pipeline
            mic.change(process_audio, inputs=mic, outputs=chatbot_ui)

            # Compiling the entire pipeline for the input / output
            _ = message_box.submit(
                TODO, inputs=[message_box, state], outputs=[chatbot_ui, state]
            )

        _ = self.gradio_block.launch(debug=True)
