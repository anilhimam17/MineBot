from typing import Literal
from pydantic import BaseModel, Field


class CraftResponse(BaseModel):
    """Structure for crafting queries."""
    response_type: Literal["CraftResponse"] = "CraftResponse"
    formula: str = Field()
    recipe: list[list[str]] = Field()
    procedure: str = Field()


class GeneralResponse(BaseModel):
    """Structure for general game queries."""
    response_type: Literal["GeneralResponse"] = "GeneralResponse"
    response: str = Field()


class GameStateResponse(BaseModel):
    """Structure for responses on providing game states."""
    # TODO