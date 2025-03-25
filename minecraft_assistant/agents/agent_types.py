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
    response_type: Literal["GameStateResponse"] = "GameStateResponse"
    response: str = Field()


class GameStateEvent(BaseModel):
    """Structure for recording game state events."""

    date: str = Field(..., alias="Date")
    time: str = Field(..., alias="Time")
    player_name: str = Field(..., alias="Player Name")
    action: str = Field(..., alias="Action")
    x_coord: int = Field(..., alias="X Coordinate")
    y_coord: int = Field(..., alias="Y Coordinate")
    z_coord: int = Field(..., alias="Z Coordinate")
    dimension: str = Field(..., alias="Dimension")
    x2_coord: str = Field("", alias="X Coordinate 2")
    y2_coord: str = Field("", alias="Y Coordinate 2")
    z2_coord: str = Field("", alias="Z Coordinate 2")
    dimension2: str = Field("", alias="Dimension 2")
    detail1: str = Field("", alias="Detail 1")
    detail2: str = Field("", alias="Detail 2")

    class Config:
        allow_population_by_field_name = True

