import re
import pandas as pd


PATH_RECIPES_DATASET = "./assets/formatted_recipes.csv"
PATH_SYSTEM_PROMPTS_DATASET = "./assets/system_prompts.csv"


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

    def load_system_prompts(self) -> str:
        """Loads all the system prompts used by the agents."""

        sys_prompts_df: pd.DataFrame = pd.read_csv(PATH_SYSTEM_PROMPTS_DATASET)
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
