from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    raw_input: str = Field(min_length=10, max_length=5000)
    description: Optional[str] = None
    target_date: Optional[date] = None
    hours_per_day: int = Field(default=2, ge=1, le=16)
    constraints: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    hours_per_day: Optional[int] = Field(default=None, ge=1, le=16)
    constraints: Optional[list[str]] = None
    context: Optional[dict[str, Any]] = None


class GoalOut(BaseModel):
    id: str
    user_id: str
    title: str
    raw_input: str
    description: Optional[str] = None
    status: str
    target_date: Optional[date] = None
    hours_per_day: int
    constraints: list[str]
    context: dict[str, Any]
    progress_percentage: float
