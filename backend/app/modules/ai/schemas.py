from pydantic import BaseModel, Field


class PlanGenerationRequest(BaseModel):
    goal: str = Field(min_length=10, max_length=5000)
    hours_per_day: int = Field(default=2, ge=1, le=16)
    constraints: list[str] = Field(default_factory=list, max_length=20)


class StageTaskSchema(BaseModel):
    title: str
    description: str | None = None
    priority: str = Field(default='medium')
    estimated_minutes: int = Field(gt=0)
    depends_on: list[str] = Field(default_factory=list)


class StageSchema(BaseModel):
    title: str
    description: str | None = None
    position: int = Field(gt=0)
    tasks: list[StageTaskSchema] = Field(default_factory=list)


class AIPlanOutput(BaseModel):
    goal_title: str
    summary: str
    assumptions: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    stages: list[StageSchema]
