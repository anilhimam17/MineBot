from typing import List, Optional, Union  # <-- Add Union import
from dataclasses import dataclass
import csv
import re
import os
import pandas as pd
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# --- 1. Search for a specific CSV file ---
def find_csv_by_pattern(directory: str, pattern: str) -> Optional[str]:
    files = [f for f in os.listdir(directory) if f.endswith('.csv') and pattern in f]
    if not files:
        return None
    elif len(files) > 1:
        print(f"Warning: Multiple matching CSV files found: {files}. Using {files[0]}")
    return os.path.join(directory, files[0])

# --- 2. Parse PlayerAction CSV ---
@dataclass
class PlayerAction:
    date: str
    time: str
    player_name: str
    action: str
    x: str
    y: str
    z: str
    dimension: str
    detail1: Optional[str] = None
    detail2: Optional[str] = None

# Read CSV data
def read_csv_to_dataclass(file_path: str) -> List[PlayerAction]:
    actions = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)  # Use DictReader to automatically parse columns by name
        for row in reader:
            try:
                action = PlayerAction(
                    date=row.get("Date", ""),
                    time=row.get("Time", ""),
                    player_name=row.get("Player Name", ""),
                    action=row.get("Action", ""),
                    x=row.get("X Coordinate", ""),
                    y=row.get("Y Coordinate", ""),
                    z=row.get("Z Coordinate", ""),
                    dimension=row.get("Dimension", ""),
                    detail1=row.get("Detail 1"),
                    detail2=row.get("Detail 2")
                )
                actions.append(action)
            except Exception as e:
                print(f"Error processing row: {e}")
    return actions

# --- 3. Extract crafted items ---
def extract_crafted_items(sentence):
    pattern = re.compile(
        r"(?:make|making|made|create|creating|created|build|building|built|craft|crafting|crafted|construct"
        r"|constructing|constructed|get|getting|got|obtain|obtaining|obtained|brew|brewing|brewed|forge|forging"
        r"|forged)\s+(?:a|an|some)?\s*(.+?)(?:\?|\.|$)|recipes? of\s+(.+?)(?:\?|\.|$)")
    match = pattern.search(sentence.lower())
    item = None
    if match:
        item = next((group for group in match.groups() if group), None)
    return item

# --- 4. Extract player queries ---
def extract_player_query(sentence: str):
    # Regular expression: Match different formats of queries
    pattern = re.compile(
        r"(?:what |where |when )\s+([\w]+)\s+(?:do|at)\s+(.+?)(?:\?|\.|$)|"  
        r"(?:what did|where did|when did)\s+([\w]+)\s+(?:do|at)\s+(.+?)(?:\?|\.|$)|"
        r"(?:what was|where was|when was)\s+([\w]+)\s+(?:do|at)\s+(.+?)(?:\?|\.|$)"
    )
    
    match = pattern.search(sentence.lower())  # Convert input sentence to lowercase
    if match:
        groups = match.groups()
        # Return the first non-empty group as player name and query time
        player_name = next((group for group in groups[::2] if group), None)  # Pick non-empty groups at indexes 0, 2, 4
        query_time = next((group for group in groups[1::2] if group), None)  # Pick non-empty groups at indexes 1, 3, 5
        return player_name, query_time
    
    return None, None

# --- 5. Display crafting table ---
def display_crafting_table(items):
    max_length = max(len(item) for item in items)
    if len(items) == 9:
        for i in range(0, 9, 3):
            row = [item.ljust(max_length) for item in items[i:i + 3]]
            print(" | ".join(row))
    elif len(items) == 10:
        # Extract crafted item and materials
        generated_item = items[0]
        grid_items = items[1:]

        # Format crafted item
        print(f"Generated Item: {generated_item}\n")

        # Print crafting grid row by row
        for i in range(0, 9, 3):
            row = [item.ljust(max_length) for item in grid_items[i:i + 3]]
            print(" | ".join(row))

# --- 6. AI interaction data structures ---
class CraftResponse(BaseModel):
    formula: str
    recipe: List[List[str]]
    procedure: str

class GeneralResponse(BaseModel):
    response: str

# --- 7. AI NLP processing ---
class NLPModel:
    def __init__(self, model_name, api_key, base_url):
        self.model = OpenAIModel(model_name, api_key=api_key, base_url=base_url)
        self.agent = None
        self.system_prompt = []
        self.response = ""

    def init_prompt(self, prompt):
        if isinstance(prompt, list):
            self.system_prompt.extend(prompt)
        elif isinstance(prompt, str):
            self.system_prompt.append(prompt)
        self.agent = Agent(
            model=self.model,
            system_prompt=self.system_prompt,
            result_type=Union[CraftResponse, GeneralResponse]  # <-- Use Union here
        )

    def chat(self, user_input):
        if self.response == "":
            self.response = self.agent.run_sync(user_input)
        else:
            self.response = self.agent.run_sync(user_input, message_history=self.response.all_messages())
        return self.response.data

# --- 8. Initialize AI model ---
model = 'deepseek-chat'
api_key = "sk-ee966d563dba4b84bff8b270c0cd267a"
url = 'https://api.deepseek.com'
chatbot = NLPModel(model, api_key, url)

# --- 9. Load prompts and player action data ---
recipes_dataset = pd.read_csv('../recipes/formated_recipes.csv', header=None)
recipes_dataset.iloc[:, 0] = recipes_dataset.iloc[:, 0].str.lower()
recipes_items = set(recipes_dataset.iloc[:, 0].values)

directory = os.path.join(os.getcwd())
player_actions_file = find_csv_by_pattern(directory, "player_actions")  # Match player action files using a keyword

# Read player actions
player_actions_list = read_csv_to_dataclass(player_actions_file) if player_actions_file else []

# Load system prompts
system_prompt = pd.read_csv('init_prompt.csv')
for i in system_prompt.index:
    chatbot.init_prompt(system_prompt.iloc[i]['message'])

# --- 10. Run chatbot ---
while True:
    user_input = input("You: ")
    if user_input.lower() in ["退出", "bye", "exit"]:
        print("AI: Bye！👋")
        break

    # Detect if the query is about Minecraft crafting
    craft_item = extract_crafted_items(user_input)
    if craft_item and craft_item in recipes_items:
        recipe = recipes_dataset[recipes_dataset.iloc[:, 0] == craft_item].values[0]
        print(recipe)
        message = (f"{','.join(recipe[1:10])}. 3x3 crafting table from left to right, top to bottom, 0 means empty. "
                   f"Output item: {craft_item}")
        user_input = message  # Modify user input with crafting info

    # Detect if the query is about player actions
    player_name, query_time = extract_player_query(user_input)
    query_time = query_time.replace('at ', '')  # Remove 'at' if present

    if query_time or player_name:
        # Find matching records
        matching_records = [a for a in player_actions_list if a.player_name.lower() == player_name.lower() or a.time.lower() == query_time]
        
        if matching_records:
            # Modify user input with the query result
            message = " | ".join([f"{action.player_name} was at ({action.x}, {action.y}, {action.z}) in {action.dimension} at {action.time} on {action.date}, performing '{action.action}'"
                                    for action in matching_records])
            user_input = message

    # Default AI interaction
    result = chatbot.chat(user_input)
    print("AI:", end=" ", flush=True)
    if isinstance(result, CraftResponse):
        print(result.formula)
        display_crafting_table([i for row in result.recipe for i in row])
        print(result.procedure)
    elif isinstance(result, GeneralResponse):
        print(result.response)

#test example
#     "What did SilentSilverL do at 04:59:12?"  