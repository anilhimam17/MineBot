import re
from typing import Any


class AgentUtilities:
    def check_crafting_query(self, user_input: str) -> Any:
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

        return result
