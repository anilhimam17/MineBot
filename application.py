from minecraft_assistant.gradio.gradio_ui import GradioInterface


class MinecraftAssistantApplication:
    def __init__(self) -> None:
        self.gradio_interface = GradioInterface()

    def run(self) -> None:
        self.gradio_interface.run()
