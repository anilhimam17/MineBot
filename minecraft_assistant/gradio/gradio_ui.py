import gradio as gr

from minecraft_assistant.agents.llm_agent import LLMAgent


# Variables to construct the agent
AGENT_NAME = "deepseek-chat"
IS_LOCAL = False


class GradioInterface:
    """Class to abstract all the gradio orchestration."""
    def __init__(self) -> None:
        self.gradio_block = gr.Blocks()
        self.llm_agent = LLMAgent(AGENT_NAME, IS_LOCAL)

    def run(self) -> None:
        """Build and run the gradio interface on localhost."""

        with self.gradio_block:
            _ = gr.Markdown(
                "<h1 style={text-align: center}>Minecraft Assistant</h1>"
            )

            chatbot_ui = gr.Chatbot()
            message_box = gr.Textbox("Let's cookup some minecraft")

            # Voice interface declaration
            # mic = gr.Audio(
            #     sources=["microphone"], type="filepath", label="Wanna, start a Chat ?"
            # )

            # # Microphone pipeline
            # mic.change(process_audio, inputs=mic, outputs=chatbot_ui)

            # Compiling the entire pipeline for the input / output
            _ = message_box.submit(
                self.llm_agent.run_pipeline, inputs=[message_box], outputs=[chatbot_ui]
            )

        _ = self.gradio_block.launch(debug=True)
