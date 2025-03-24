from typing import Annotated, Any
from pydantic import Field
from pydantic_ai import Agent
from minecraft_assistant.agents.agent_types import CraftResponse, GeneralResponse
from minecraft_assistant.agents.agent_utils import AgentUtilities

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


# Generic Datatype that is returned by the models
ResultDepsT = Annotated[CraftResponse | GeneralResponse, Field(discriminator="response_type")]


class LLMAgent:
    """Implements all the functionalities required for the AI Agents."""

    def __init__(self, agent_name: str, is_local: bool) -> None:
        self.is_local = is_local
        self.agent_utilities = AgentUtilities()
        system_prompt = self.agent_utilities.load_system_prompts()

        if self.is_local:
            ollama_agent = OpenAIModel(
                agent_name, provider=OpenAIProvider(base_url='http://localhost:11434/v1', api_key="local_key")
            )
            self.pydantic_ai_agent = Agent(
                ollama_agent, system_prompt=system_prompt, result_type=ResultDepsT, retries=3
            )
        else:
            if agent_name == "deepseek-chat":
                deepseek_agent = OpenAIModel(
                    agent_name, provider=OpenAIProvider('https://api.deepseek.com', api_key="sk-ee966d563dba4b84bff8b270c0cd267a")
                )
                self.pydantic_ai_agent = Agent(
                    deepseek_agent, system_prompt=system_prompt, result_type=ResultDepsT
                )
            # elif "gemini" in agent_name:

            #     # Alternate result type for Gemini Compatibility
            #     ResultDepsT = CraftResponse | GeneralResponse

            #     gemini_agent = GeminiModel(agent_name)
            #     self.pydantic_ai_agent = Agent(
            #         gemini_agent, system_prompt=system_prompt, result_type=ResultDepsT
            #     )

    def run_query(self, user_input: str) -> Any:
        """Makes a request to the the AI Agent to generate a response."""

        prompt, query_craft_type = self.process_input(user_input)

        try:
            response = self.pydantic_ai_agent.run_sync(prompt)
            return response.data
        except Exception as ex:
            print(f"Attempt failed with: {ex}, Simplifying the approach ....")

    def process_input(self, user_input: str) -> tuple[str, bool]:
        """Processes the input string from the user and returns a context aware prompt."""

        # Check the query for Crafting
        is_craft = False
        craft_item = self.agent_utilities.check_crafting_query(user_input=user_input)
        if craft_item and craft_item in self.agent_utilities.recipe_items:

            # Finding the recipe to provide RAG
            recipe = self.agent_utilities.recipes_dataset[
                self.agent_utilities.recipes_dataset.iloc[:, 0] == craft_item
            ]
            recipe = recipe.values[0]

            # Context aware prompt
            prompt = (
                f"{','.join(recipe[1:10])}. 3 by 3 2D array crafting table based on the above nine elements "
                f"from left to right and from top to bottom in sequence, 0 means empty. Output item is {craft_item}"
            )

            # Flag for Crafting Queries
            is_craft = True
        else:
            prompt = user_input

        return (prompt, is_craft)


# Testing
gemini_model = "google-gla:gemini-2.0-pro-exp-02-05"
deepseek_model = "deepseek-chat"
llama3_2 = "qwen2.5:7b"
minecraft_agent = LLMAgent(llama3_2, True)

prompt_1 = minecraft_agent.process_input("How to craft a stone sword ?")
prompt_2 = minecraft_agent.process_input("Where can I find diamonds ?")

result_1 = minecraft_agent.run_query(prompt_1[0])
print(result_1, end="\n\n")

result_2 = minecraft_agent.run_query(prompt_2[0])
print(result_2, end="\n\n")
