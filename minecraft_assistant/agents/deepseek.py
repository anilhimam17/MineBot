import re
from typing import Any, Union
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from minecraft_assistant.agents.agent_utils import CraftResponse, GeneralResponse


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


def is_craft_query(user_query: str) -> Any:
    """Identifying crafting queries apart from general queries providing context."""

    # Raw string for all crafting verbs
    craft_verbs = (
        r"(?:"
        r"make|making|made|"
        r"create|creating|created|"
        r"build|building|built|"
        r"craft|crafting|crafted|"
        r"construct|constructing|constructed|"
        r"get|getting|got|"
        r"obtain|obtaining|obtained|"
        r"brew|brewing|brewed|"
        r"forge|forging|forged"
        r")"
    )

    # Raw string for quantity
    articles = r"(?:a|an|some)?"

    # Item pattern search raw string
    item_pattern = fr"{craft_verbs}\s+{articles}\s*(.+?)(?:\?|\.|$)"

    # Recipe pattern search raw string
    recipe_pattern = r"recipes? of \s+(.+?)(?:\?|\.|$)"

    # Compiled Regular Expression
    query_pattern = re.compile(f"{item_pattern}|{recipe_pattern}")

    # Regex Search
    match = query_pattern.search(user_query.lower())

    item = None
    if match:
        item= next((group for group in match.groups() if group), None)
    return item

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
            self.system_prompt.extend(i)
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


# text example
# [
#     "How to create a Nether portal?",
#     "What are the steps to forge a diamond sword?",
#     "Can you tell me how to build a wooden house?",
#     "I want to make a furnace.",
#     "How can I craft TNT?",
#     "What do I need to build a shield?",
# ]