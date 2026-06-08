import datetime
from typing import Literal
from src.domain.enum.task_status_enum import TaskEnum
from pydantic import BaseModel

class TaskStatus(BaseModel):
    task_id: int
    status: TaskEnum
    updated_at: datetime
    created_at: datetime
