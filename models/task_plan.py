from pydantic import BaseModel
from models.tool_plan import ToolPlan

class TaskPlan(BaseModel):
    steps: list[ToolPlan]