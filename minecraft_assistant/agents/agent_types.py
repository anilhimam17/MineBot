from pydantic import BaseModel


class CraftResponse(BaseModel):
    """Structure for crafting queries."""
    formula: str
    recipe: list[list[str]]
    procedure: str


class GeneralResponse(BaseModel):
    """Structure for general game queries."""
    response: str


# Generic result type for different responses
ResultDepsT = CraftResponse | GeneralResponse
