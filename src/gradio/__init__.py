import gradio as gr
import pandas as pd
from difflib import get_close_matches

# Load the dataset
file_path = r"C:\Users\harin\Downloads\formated_recipes.csv"
df = pd.read_csv(file_path, header=None)

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

        import random
        return random.choice(responses)

    return "🤔 Hmm... I couldn't find that recipe! Maybe try a common item like 'torch' or 'pickaxe'? 🔍"

# Create a Chat Interface with Gradio
chatbot = gr.ChatInterface(
    chatbot_response,
    title="Minecraft Crafting Assistant 🏗️",
    description="Ask about Minecraft crafting recipes in a chat format! Example: 'How do I craft a pickaxe?'",
    theme="default",
)

# Launch the chatbot
chatbot.launch()