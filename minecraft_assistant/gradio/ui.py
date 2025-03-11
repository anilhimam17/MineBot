import gradio as gr
import pandas as pd
from difflib import get_close_matches
import os
import random
import json
from typing import List

# Load the dataset with error handling
file_path = os.path.join(os.getcwd(), "assets", "formatted_recipes.csv")

try:
    df = pd.read_csv(file_path, header=None)
except Exception as e:
    raise FileNotFoundError(f"Failed to load dataset: {e}")

# Convert dataset into a structured dictionary
crafting_recipes = {}

for _, row in df.iterrows():
    item_name = row[0].strip().lower()  # Crafted item
    
    # Extract 3x3 crafting grid (Columns 1 to 9)
    crafting_grid = [row[1:4].tolist(), row[4:7].tolist(), row[7:10].tolist()]

    # Store in dictionary
    crafting_recipes[item_name] = {
        "output": item_name.capitalize(),
        "crafting_grid": crafting_grid
    }

# MessageDataStore Class (to store chat history)
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class MessageDataStore:
    # Message Store
    message_store: List[str] = field(default_factory=list)

    # Class Variables
    n_past_messages: ClassVar[int] = 5  # Keep last 5 messages by default

    def add_message(self, message: str) -> None:
        self.message_store.append(message)

    def load_past_messages(self) -> List[str]:
        start_idx = len(self.message_store) - self.n_past_messages
        return self.message_store[start_idx:]


# Simulate a database for storing chat history (using MessageDataStore)
class ChatDatabase:
    def __init__(self, filename="chat_history.json"):
        self.filename = filename
        self.chat_history = MessageDataStore()

    def add_message(self, message, response):
        self.chat_history.add_message(f"User: {message}")
        self.chat_history.add_message(f"Bot: {response}")
        self.save_chat_history()

    def get_chat_history(self):
        return self.chat_history.message_store

    def save_chat_history(self):
        # Save chat history to a JSON file
        with open(self.filename, "w") as f:
            json.dump(self.chat_history.message_store, f, indent=4)

    def load_chat_history(self):
        # Load chat history from a JSON file (if it exists)
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                messages = json.load(f)
                for message in messages:
                    self.chat_history.add_message(message)
        else:
            return []

# Initialize the in-memory database
chat_db = ChatDatabase()

# AI Chatbot Function
def chatbot_response(message, chat_history):
    user_input = message.lower().strip()

    # Find the closest match
    matched_item = None
    if user_input in crafting_recipes:
        matched_item = user_input
    else:
        close_matches = get_close_matches(user_input, crafting_recipes.keys(), n=1, cutoff=0.7)
        if close_matches:
            matched_item = close_matches[0]  # Pick the best match

    # If a match is found, return the recipe with a friendly response
    if matched_item:
        recipe = crafting_recipes[matched_item]
        grid = "\n".join([" | ".join(str(cell) for cell in row) for row in recipe["crafting_grid"]])

        responses = [
            f"🎉 Great choice! Here's how you craft a **{recipe['output']}**:\n\n"
            f"🛠️ **Crafting Table Layout:**\n\n{grid}\n\n"
            f"Go ahead and give it a try! 🚀",

            f"Ah, looking to craft a **{recipe['output']}**? No problem! Here's what you need:\n\n"
            f"🛠️ **Crafting Grid:**\n\n{grid}\n\n"
            f"Hope that helps! Happy crafting! 🎮",

            f"Crafting a **{recipe['output']}**? Gotcha! Here's the layout:\n\n"
            f"\n{grid}\n\n"
            f"Let me know if you need another recipe! 😊"
        ]

        # Store the message and response in the database
        chat_db.add_message(message, random.choice(responses))

        return random.choice(responses)

    return "🤔 Hmm... I couldn't find that recipe! Maybe try a common item like 'torch' or 'pickaxe'? 🔍"

# Create a Gradio chat interface
def gradio_chatbot(message, chat_history):
    response = chatbot_response(message, chat_history)
    # Append new message and response to history (simulated as in the database)
    return "", chat_db.get_chat_history()  # Get chat history from the "database"

# Generate script to replay the chat history
def generate_script():
    chat_history = chat_db.get_chat_history()
    script_lines = [
        "import gradio as gr",
        "import random",
        "def chatbot_response(message):",
        "    # Your response logic goes here...",
        "    return \"This is a placeholder response.\"\n"
    ]
    
    # Add each chat message to the script
    for message in chat_history:
        script_lines.append(f'# {message}')

    script_content = "\n".join(script_lines)
    script_filename = os.path.join(os.getcwd(), "replay_chat_history.py")
    with open(script_filename, "w") as script_file:
        script_file.write(script_content)
    
    print(f"Script generated and saved as {script_filename}")

# Launch the chatbot with a Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("### Minecraft Crafting Assistant 🏗️\nAsk about Minecraft crafting recipes!")
    chat_history = gr.State()  # state for keeping track of chat
    chatbot = gr.Chatbot()  # Instantiate Chatbot directly
    textbox = gr.Textbox(placeholder="Ask me about a crafting recipe...", lines=1)
    
    textbox.submit(gradio_chatbot, [textbox, chat_history], [chat_history, chatbot])
    generate_script_button = gr.Button("Generate Script")
    generate_script_button.click(generate_script)

demo.launch()
