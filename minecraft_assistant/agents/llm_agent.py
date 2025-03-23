import re
from typing import Any, Literal
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from minecraft_assistant.agents.agent_types import ResultDepsT


class LLMAgent:
    """Implements all the functionalities required for the AI Agents."""

    def __init__(self, agent_name: str, is_local: bool, system_prompt: list[str]) -> None:
        if is_local:
            ollama_agent = OpenAIModel(
                agent_name, provider=OpenAIProvider(base_url='http://localhost:11434/v1')
            )
            self.pydantic_ai_agent = Agent(
                ollama_agent, system_prompt=system_prompt, result_type=type[ResultDepsT]
            )
        else:
            self.pydantic_ai_agent = Agent(
                agent_name, system_prompt=system_prompt, result_type=type[ResultDepsT]
            )

    def run_query(self, user_input: Any) -> Any:
        """Makes a request to the the AI Agent to generate a response."""

        response = self.pydantic_ai_agent.run_sync(
            user_input
        )
        return response.data

    def process_input(self, user_input: str) -> str:
        """Processes the input string from the user and returns a context aware prompt."""
        return ""
