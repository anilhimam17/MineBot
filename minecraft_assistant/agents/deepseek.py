import re
from pydantic import BaseModel
from typing import Union, List
import pandas as pd
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

recipes_dataset = pd.read_csv('../recipes/formated_recipes.csv', header=None)
recipes_dataset.iloc[:, 0] = recipes_dataset.iloc[:, 0].str.lower()
recipes_items = set(recipes_dataset.iloc[:, 0].values)


def display_crafting_table(items):
    max_length = max(len(item) for item in items)
    if len(items) == 9:
        for i in range(0, 9, 3):
            row = [item.ljust(max_length) for item in items[i:i + 3]]
            print(" | ".join(row))
    elif len(items) == 10:
        # 提取生成物品和合成材料
        generated_item = items[0]
        grid_items = items[1:]

        # 格式化生成物品
        print(f"Generated Item: {generated_item}\n")

        # 逐行打印合成表
        for i in range(0, 9, 3):
            row = [item.ljust(max_length) for item in grid_items[i:i + 3]]
            print(" | ".join(row))


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


class CraftResponse(BaseModel):
    formula: str
    # recipe: str
    recipe: List[List[str]]
    procedure: str


# class Response(BaseModel):
#     language: str
#     code: str


class GeneralResponse(BaseModel):
    response: str


class NLPModel:

    def __init__(self, model_name, api_key, base_url):
        self.model = OpenAIModel(
            model_name,
            api_key=api_key,
            base_url=base_url,

        )
        self.agent = None
        self.system_prompt = []
        self.response = ""

    def init_prompt(self, prompt):
        if isinstance(prompt, list):
            for i in prompt:
                self.system_prompt.append(i)
        elif isinstance(prompt, str):
            self.system_prompt.append(prompt)
        self.agent = Agent(
            model=self.model,
            system_prompt=self.system_prompt,  # 传入系统提示
            result_type=Union[CraftResponse, GeneralResponse]
        )

    def chat(self, user_input):
        if self.response == "":
            self.response = self.agent.run_sync(user_input)
        else:
            self.response = self.agent.run_sync(user_input, message_history=self.response.all_messages())

        return self.response.data


model = 'deepseek-chat'
api_key = "sk-ee966d563dba4b84bff8b270c0cd267a"
url = 'https://api.deepseek.com'
chatbot = NLPModel(model, api_key, url)

system_prompt = pd.read_csv('init_prompt.csv')
for i in system_prompt.index:
    chatbot.init_prompt(system_prompt.iloc[i]['message'])

while True:

    user_input = input("You: ")
    if user_input.lower() in ["退出", "bye", "exit"]:
        print("AI: Bye！👋")
        break

    craft_item = extract_crafted_items(user_input)
    if craft_item and (craft_item in recipes_items):
        recipe = recipes_dataset[recipes_dataset.iloc[:, 0] == craft_item].values[0]
        # print(recipe)
        # recipe form
        message = (f"{','.join(recipe[1:10])}. 3 by 3 2D array crafting table based on the above nine elements"
                   f"from left to right and from top to bottom in sequence, 0 means empty output item is {craft_item}")
        # simple reply
        # message = f"{','.join(recipe)}. Crafting based on the above nine elements.{user_input}"
        # display_crafting_table(recipe)
        user_input = message
        # print(message)
    result = chatbot.chat(user_input)
    print("AI:", end=" ", flush=True)
    if isinstance(result, CraftResponse):
        print(result.formula)
        # print(result.recipe)  # string recipe
        # print(*result.recipe, sep="\n")
        display_crafting_table([i for row in result.recipe for i in row])
        print(result.procedure)
    elif isinstance(result, GeneralResponse):
        print(result.response)

# text example
# [
#     "How to create a Nether portal?",
#     "What are the steps to forge a diamond sword?",
#     "Can you tell me how to build a wooden house?",
#     "I want to make a furnace.",
#     "How can I craft TNT?",
#     "What do I need to build a shield?",
# ]