from pydantic import BaseModel


class CraftResponse(BaseModel):
    formula: str
    # recipe: str
    recipe: list[list[str]]
    procedure: str


class GeneralResponse(BaseModel):
    response: str
