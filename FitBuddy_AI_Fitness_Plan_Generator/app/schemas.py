from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

Goal = Literal["Weight loss", "Muscle gain", "General wellness", "Flexibility"]
Intensity = Literal["Low", "Medium", "High"]
Experience = Literal["Beginner", "Intermediate", "Advanced"]


class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    username: str = Field(min_length=2, max_length=120)
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=16, le=100)
    weight: float = Field(gt=20, le=350)
    goal: Goal
    intensity: Intensity
    experience: Experience = "Beginner"


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=5, max_length=1000)
