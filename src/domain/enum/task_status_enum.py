from enum import Enum

class TaskEnum(str, Enum):
    pending = "PENDING"
    processing = "PROCESSING"
    completed = "COMPLETED"
    failed = "FAILED"