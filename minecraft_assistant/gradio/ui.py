import gradio as gr
import pandas as pd
import os
import json
from minecraft_assistant.dialogue_space.message_datastore import MessageDataStore
from minecraft_assistant.agents.deepseek import NLPModel, is_craft_query, display_crafting_table
from minecraft_assistant.agents.agent_utils import CraftResponse, GeneralResponse


# Simulate a database for storing chat history (using MessageDataStore)
class ChatDatabase:
    def __init__(self, filename="./logs/chat_history.json"):
        self.filename = filename
        self.chat_history = MessageDataStore()

    def add_message(self, message, response):
        self.chat_history.add_message(f"User: {message}")
        self.chat_history.add_message(f"Bot: {response}")
        self.save_chat_history()

    def get_chat_history(self):
        return "\n".join(self.chat_history.message_store)

    def save_chat_history(self):
        with open(self.filename, "w") as f:
            json.dump(self.chat_history.message_store, f, indent=4)

    def load_chat_history(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                messages = json.load(f)
                for message in messages:
                    self.chat_history.add_message(message)


# Initialize the in-memory database
chat_db = ChatDatabase()
chat_db.load_chat_history()

# Loading the Recipe Dataset
recipes_dataset: pd.DataFrame = pd.read_csv('./assets/formatted_recipes.csv', header=None)
recipes_dataset.iloc[:, 0] = recipes_dataset.iloc[:, 0].str.lower()
recipes_items = set(recipes_dataset.iloc[:, 0].values)

# Initialise the AI Agent
model = 'deepseek-chat'
api_key = "sk-ee966d563dba4b84bff8b270c0cd267a"
url = 'https://api.deepseek.com'
chatbot = NLPModel(model, api_key, url)

# Load system prompts
system_prompt = pd.read_csv('./assets/init_prompt.csv')
for i in system_prompt.index:
    chatbot.init_prompt(system_prompt.iloc[i]['message'])


def chat_with_ai(user_input, history):
    history = history or []
    
    # Exit condition
    if user_input.lower() in ["退出", "bye", "exit"]:
        response = "AI: Bye！👋"
        history.append((user_input, response))
        return history, history

    # Check if it's a crafting query
    craft_item = is_craft_query(user_input)
    if craft_item and (craft_item in recipes_items):
        recipe = recipes_dataset[recipes_dataset.iloc[:, 0] == craft_item].values[0]
        message = (
            f"{','.join(recipe[1:10])}. 3 by 3 2D array crafting table based on the above nine elements "
            f"from left to right and from top to bottom in sequence, 0 means empty. Output item is {craft_item}"
        )
    else:
        message = user_input

    # Get response from the chatbot
    result = chatbot.chat(message)

    if isinstance(result, CraftResponse):
        response = f"{result.formula}\n{result.procedure}"
    elif isinstance(result, GeneralResponse):
        response = result.response
    else:
        response = "I'm not sure how to respond to that."

    # Add to chat history
    chat_db.add_message(user_input, response)
    history.append((user_input, response))
    return history, history


# Gradio Interface
block = gr.Blocks()

with block:
    gr.Markdown("""<h1><center>Minecraft Assistant Chatbot</center></h1>""")
    chatbot_ui = gr.Chatbot()
    message = gr.Textbox(placeholder="Type your message here...")
    state = gr.State()
    submit = gr.Button("SEND")
    submit.click(chat_with_ai, inputs=[message, state], outputs=[chatbot_ui, state])

block.launch(debug=True)