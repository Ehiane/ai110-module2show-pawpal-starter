from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class PriorityLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Frequency(Enum):
    ONCE = "Once"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


@dataclass
class Task:
    description: str
    time: datetime
    priority: PriorityLevel
    frequency: Frequency
    duration: int
    pet: 'Pet'
    owner_preferences: Dict = field(default_factory=dict)
    is_completed: bool = False
    task_id: UUID = field(default_factory=uuid4)
    schedule: Optional['Schedule'] = None

    def get_task_time(self) -> datetime:
        """Return the task's scheduled time."""
        return self.time

    def get_priority_level(self) -> PriorityLevel:
        """Return the task's priority level."""
        return self.priority

    def get_owner_preferences(self) -> Dict:
        """Return the owner's preferences for this task."""
        return self.owner_preferences

    def get_task_duration(self) -> int:
        """Return the task's duration in minutes."""
        return self.duration

    def get_description(self) -> str:
        """Return the task's description."""
        return self.description

    def get_frequency(self) -> Frequency:
        """Return how often the task recurs."""
        return self.frequency

    def get_pet(self) -> 'Pet':
        """Return the pet this task applies to."""
        return self.pet

    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self.is_completed = True

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.is_completed = False

    def is_task_completed(self) -> bool:
        """Return whether the task is completed."""
        return self.is_completed


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    owner: 'Owner'
    pet_id: UUID = field(default_factory=uuid4)

    def get_owner(self) -> 'Owner':
        """Return the pet's owner."""
        return self.owner

    def get_name(self) -> str:
        """Return the pet's name."""
        return self.name

    def get_breed(self) -> str:
        """Return the pet's breed."""
        return self.breed

    def get_age(self) -> int:
        """Return the pet's age in years."""
        return self.age

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.owner.get_tasks_for_pet(self)

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks for this pet."""
        return [task for task in self.get_tasks() if not task.is_completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return all completed tasks for this pet."""
        return [task for task in self.get_tasks() if task.is_completed]


@dataclass
class Schedule:
    pet: Pet
    tasks: List[Task] = field(default_factory=list)
    schedule_id: UUID = field(default_factory=uuid4)

    def get_tasks(self) -> List[Task]:
        """Return all tasks in this schedule for the associated pet."""
        return [task for task in self.tasks if task.pet == self.pet]

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule (must belong to the same pet)."""
        if task.pet != self.pet:
            raise ValueError(f"Task is for {task.pet.get_name()}, not {self.pet.get_name()}")
        if task not in self.tasks:
            task.schedule = self
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_pet(self) -> Pet:
        """Return the pet this schedule is for."""
        return self.pet

    def get_tasks_by_priority(self, priority: PriorityLevel) -> List[Task]:
        """Return all tasks in this schedule filtered by priority level."""
        return [task for task in self.get_tasks() if task.priority == priority]

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks in this schedule."""
        return [task for task in self.get_tasks() if not task.is_completed]


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    schedules: List[Schedule] = field(default_factory=list)
    owner_id: UUID = field(default_factory=uuid4)

    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's collection."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_tasks(self) -> List[Task]:
        """Return all tasks across all schedules for all pets."""
        all_tasks = []
        for schedule in self.schedules:
            all_tasks.extend(schedule.get_tasks())
        return all_tasks

    def get_tasks_by_priority(self, priority: PriorityLevel) -> List[Task]:
        """Return all tasks filtered by priority level."""
        return [task for task in self.get_tasks() if task.priority == priority]

    def get_tasks_for_pet(self, pet: Pet) -> List[Task]:
        """Return all tasks specific to a pet owned by this owner."""
        if pet not in self.pets:
            raise ValueError(f"Pet {pet.get_name()} does not belong to this owner")
        return [task for task in self.get_tasks() if task.pet == pet]

    def get_owner_id(self) -> UUID:
        """Return the owner's unique identifier."""
        return self.owner_id

    def get_name(self) -> str:
        """Return the owner's name."""
        return self.name

    def add_schedule(self, schedule: Schedule) -> None:
        """Add a schedule for one of the owner's pets."""
        if schedule.pet not in self.pets:
            raise ValueError(f"Schedule's pet {schedule.pet.get_name()} is not owned by this owner")
        if schedule not in self.schedules:
            self.schedules.append(schedule)

    def get_all_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks across all pets."""
        return [task for task in self.get_tasks() if not task.is_completed]

    def get_all_completed_tasks(self) -> List[Task]:
        """Return all completed tasks across all pets."""
        return [task for task in self.get_tasks() if task.is_completed]


class Scheduler:
    """The brain of the system that retrieves, organizes, and manages tasks across all pets and owners."""

    def __init__(self):
        """Initialize an empty scheduler."""
        self.owners: List[Owner] = []

    def add_owner(self, owner: Owner) -> None:
        """Add an owner to the scheduler's management."""
        if owner not in self.owners:
            self.owners.append(owner)

    def remove_owner(self, owner: Owner) -> None:
        """Remove an owner from the scheduler's management."""
        if owner in self.owners:
            self.owners.remove(owner)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks from all owners."""
        all_tasks = []
        for owner in self.owners:
            all_tasks.extend(owner.get_tasks())
        return all_tasks

    def get_all_tasks_for_owner(self, owner: Owner) -> List[Task]:
        """Return all tasks for a specific owner."""
        return owner.get_tasks()

    def get_pending_tasks_for_owner(self, owner: Owner) -> List[Task]:
        """Return all incomplete tasks for a specific owner."""
        return owner.get_all_pending_tasks()

    def get_completed_tasks_for_owner(self, owner: Owner) -> List[Task]:
        """Return all completed tasks for a specific owner."""
        return owner.get_all_completed_tasks()

    def get_tasks_by_priority_for_owner(self, owner: Owner, priority: PriorityLevel) -> List[Task]:
        """Return tasks for a specific owner filtered by priority."""
        return owner.get_tasks_by_priority(priority)

    def get_tasks_for_pet(self, pet: Pet) -> List[Task]:
        """Return all tasks for a specific pet."""
        return pet.get_owner().get_tasks_for_pet(pet)

    def get_pending_tasks_for_pet(self, pet: Pet) -> List[Task]:
        """Return all incomplete tasks for a specific pet."""
        return pet.get_pending_tasks()

    def get_completed_tasks_for_pet(self, pet: Pet) -> List[Task]:
        """Return all completed tasks for a specific pet."""
        return pet.get_completed_tasks()

    def get_tasks_by_frequency(self, frequency: Frequency) -> List[Task]:
        """Return all tasks filtered by recurrence frequency."""
        return [task for task in self.get_all_tasks() if task.frequency == frequency]

    def get_tasks_sorted_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by priority (HIGH -> MEDIUM -> LOW), optionally from a custom list."""
        if tasks is None:
            tasks = self.get_all_tasks()
        priority_order = {PriorityLevel.HIGH: 0, PriorityLevel.MEDIUM: 1, PriorityLevel.LOW: 2}
        return sorted(tasks, key=lambda t: priority_order[t.priority])

    def get_tasks_sorted_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted chronologically by scheduled time."""
        if tasks is None:
            tasks = self.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def get_overdue_tasks(self, current_time: datetime) -> List[Task]:
        """Return all incomplete tasks with scheduled times before or at the current time."""
        return [task for task in self.get_all_tasks() if task.time <= current_time and not task.is_completed]

    def mark_task_completed(self, task: Task) -> None:
        """Mark a task as completed."""
        task.mark_completed()
