import re
import pandas as pd

from minecraft_assistant.agents.agent_types import GameStateEvent


PATH_GAME_STATE_DATASET = "./assets/game_states.csv"
PATH_RECIPES_DATASET = "./assets/formatted_recipes.csv"
PATH_SYSTEM_PROMPTS_DATASET_OPEN = "./assets/system_prompts_open.csv"
PATH_SYSTEM_PROMPTS_DATASET_CLOSED = "./assets/system_prompts_closed.csv"


class AgentUtilities:
    @property
    def recipes_dataset(self) -> pd.DataFrame:
        """Loads the dataset for recipes to improves the context of the Agent."""

        recipes_df = pd.read_csv(PATH_RECIPES_DATASET, header=None)
        recipes_df.iloc[:, 0] = recipes_df.iloc[:, 0].str.lower()
        return recipes_df

    @property
    def recipe_items(self) -> set[str]:
        """Loads the names of the recipes."""

        return set(self.recipes_dataset.iloc[:, 0].values)

    def load_game_state_events(self) -> list:
        """Loads the game state events in real-time"""
        # Define conversion functions for integer fields.
        def to_int(val: str) -> int:
            try:
                # Remove any spaces and check if value is a digit (allow negative sign)
                val = val.strip()
                if val.lstrip('-').isdigit():
                    return int(val)
                # You can add more specific conversions here if needed.
            except Exception:
                pass
            # Return zero if conversion fails
            return 0

        # Define converters for relevant columns.
        converters = {
            "X Coordinate": to_int,
            "Y Coordinate": to_int,
            "Z Coordinate": to_int,
            # If the secondary coordinate columns are expected as strings, leave them, or add similar converters.
            "X Coordinate 2": lambda x: x if isinstance(x, str) and x != "-" else "",
            "Y Coordinate 2": lambda x: x if isinstance(x, str) and x != "-" else "",
            "Z Coordinate 2": lambda x: x if isinstance(x, str) and x != "-" else "",
            # For detail fields, replace nan or "-" with an empty string.
            "Detail 1": lambda x: x if x not in [None, "nan", "-"] else "",
            "Detail 2": lambda x: x if x not in [None, "nan", "-"] else "",
        }

        game_state_df = pd.read_csv(PATH_GAME_STATE_DATASET, converters=converters, on_bad_lines="skip")

        events = []
        for index, row in game_state_df.iterrows():
            # Convert pandas NaN to an empty string for string fields.
            row_dict = row.to_dict()
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = ""
            try:
                # Validate using the GameStateEvent model.
                event = GameStateEvent.model_validate(row_dict)
                events.append(event)
            except Exception as ex:
                print(f"Error failed with: {ex} for index {index}")
        return events

    def load_system_prompts(self, is_local: bool) -> str:
        """Loads all the system prompts used by the agents."""

        if is_local:
            sys_prompts_df: pd.DataFrame = pd.read_csv(PATH_SYSTEM_PROMPTS_DATASET_OPEN)
        else:
            sys_prompts_df: pd.DataFrame = pd.read_csv(PATH_SYSTEM_PROMPTS_DATASET_CLOSED)

        systems_prompts: list[str] = [sys_prompts_df.iloc[i]["message"] for i in sys_prompts_df.index]
        entire_prompt = " ".join(systems_prompts)

        return entire_prompt

    def check_crafting_query(self, user_input: str) -> str | None:
        """Checking for a crafting question in user_input."""

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

        matches = query_pattern.search(user_input.lower())
        result = None
        if matches:
            result = next((group for group in matches.groups() if group), None)

        return result.strip() if result else None
