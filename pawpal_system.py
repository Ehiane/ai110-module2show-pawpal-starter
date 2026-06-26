from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class PriorityLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Task:
    time: datetime
    priority: PriorityLevel
    owner_preferences: Dict
    duration: int
    task_id: UUID = field(default_factory=uuid4)

    def get_task_time(self) -> datetime:
        return self.time

    def get_priority_level(self) -> PriorityLevel:
        return self.priority

    def get_owner_preferences(self) -> Dict:
        return self.owner_preferences

    def get_task_duration(self) -> int:
        return self.duration


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    owner: 'Owner'
    pet_id: UUID = field(default_factory=uuid4)

    def get_owner(self) -> 'Owner':
        return self.owner

    def get_name(self) -> str:
        return self.name

    def get_breed(self) -> str:
        return self.breed

    def get_age(self) -> int:
        return self.age


@dataclass
class Schedule:
    tasks: List[Task] = field(default_factory=list)
    schedule_id: UUID = field(default_factory=uuid4)

    def get_tasks(self) -> List[Task]:
        return self.tasks


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    schedules: List[Schedule] = field(default_factory=list)
    owner_id: UUID = field(default_factory=uuid4)

    def get_pets(self) -> List[Pet]:
        return self.pets

    def get_tasks(self) -> List[Task]:
        all_tasks = []
        for schedule in self.schedules:
            all_tasks.extend(schedule.get_tasks())
        return all_tasks

    def get_owner_id(self) -> UUID:
        return self.owner_id

    def get_name(self) -> str:
        return self.name
