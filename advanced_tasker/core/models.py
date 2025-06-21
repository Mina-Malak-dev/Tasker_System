from datetime import datetime
from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Task:
    def __init__(self):
        self.id = None
        self.title = ""
        self.description = ""
        self.category = ""
        self.priority = Priority.MEDIUM
        self.due_date = None
        self.created_at = datetime.now()
        self.completed = False
        self.recurring = False
        self.recurrence_pattern = ""
        self.time_spent = 0
        self.attachments = []