from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4
from copy import copy


class PriorityLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Frequency(Enum):
    ONCE = "Once"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


PRIORITY_ORDER = {PriorityLevel.HIGH: 0, PriorityLevel.MEDIUM: 1, PriorityLevel.LOW: 2}
FREQUENCY_STEP = {Frequency.DAILY: 1, Frequency.WEEKLY: 7, Frequency.MONTHLY: 30}


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

    def get_end_time(self) -> datetime:
        """Return the task's end time (start time + duration)."""
        return self.time + timedelta(minutes=self.duration)

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


def has_conflict(task1: Task, task2: Task) -> bool:
    """Check if two tasks overlap in time (same pet, overlapping windows).

    Returns True if both tasks are for the same pet AND their time windows overlap.
    Handles the case where task1 starts before task2 starts but ends during task2,
    or any other overlap scenario. Returns False for different pets (no conflict).

    Args:
        task1: First task to compare
        task2: Second task to compare

    Returns:
        bool: True if tasks conflict (same pet + time overlap), False otherwise
    """
    if task1.pet != task2.pet or task1.task_id == task2.task_id:
        return False

    return not (task1.get_end_time() <= task2.time or task2.get_end_time() <= task1.time)


def expand_recurring_task(task: Task, num_days: int) -> List[Task]:
    """Generate task instances from a recurring pattern over a time window.

    Converts a single recurring task definition into multiple task instances,
    one for each occurrence within the given time window. Each instance has a
    unique task_id but preserves the original task's properties.

    Args:
        task: The task with a frequency pattern (ONCE, DAILY, WEEKLY, MONTHLY)
        num_days: Number of days ahead to expand

    Returns:
        List[Task]: Task instances. ONCE returns [task], DAILY returns ~num_days
                    instances, WEEKLY returns ~num_days/7 instances, etc.

    Example:
        A DAILY task over 7 days expands to 7 instances at daily intervals.
        A WEEKLY task over 7 days expands to 1 instance (itself).
    """
    if task.frequency == Frequency.ONCE:
        return [task]

    step = FREQUENCY_STEP.get(task.frequency, 1)
    instances = []

    for i in range(0, num_days, step):
        new_task = copy(task)
        new_task.time = task.time + timedelta(days=i)
        new_task.task_id = uuid4()
        instances.append(new_task)

    return instances


def find_all_conflicts(tasks: List[Task]) -> List[Tuple[Task, Task]]:
    """Find all conflicting task pairs in a list.

    Identifies every pair of tasks that cannot coexist (same pet, overlapping times).
    Optimized by grouping tasks by pet ID first, avoiding O(n²) cross-pet comparisons
    where cross-pet tasks can never conflict.

    Args:
        tasks: List of all tasks to check for conflicts

    Returns:
        List[Tuple[Task, Task]]: List of (task1, task2) pairs where both tasks
                                overlap in time and are for the same pet.

    Time Complexity:
        Worst case: O(n²) when all tasks are for one pet.
        Average case: Much better when tasks are distributed across multiple pets.
    """
    conflicts = []
    by_pet_id = {}
    for task in tasks:
        pet_id = id(task.pet)
        if pet_id not in by_pet_id:
            by_pet_id[pet_id] = []
        by_pet_id[pet_id].append(task)

    for pet_tasks in by_pet_id.values():
        for i, t1 in enumerate(pet_tasks):
            for t2 in pet_tasks[i+1:]:
                if has_conflict(t1, t2):
                    conflicts.append((t1, t2))
    return conflicts


def sort_by_time(tasks: List[Task]) -> List[Task]:
    """Sort tasks chronologically with today's tasks prioritized first.

    Creates a sort key tuple (days_from_today, time_of_day) that ensures:
    - Today's tasks appear first (days_diff = 0)
    - Within same day, tasks are sorted by time of day
    - Future tasks appear in chronological order

    Args:
        tasks: List of tasks to sort

    Returns:
        List[Task]: Tasks sorted chronologically, with today's tasks first

    Example:
        Input: [6PM task, 9AM task, 8AM task, 5PM task, 12PM task, 3PM task]
        Output: [8AM task, 9AM task, 12PM task, 3PM task, 5PM task, 6PM task]
    """
    today = datetime.now().date()
    return sorted(tasks, key=lambda t: ((t.time.date() - today).days, t.time.time()))


class TaskQuery:
    """Composable filter/sort pipeline for tasks (fluent API pattern).

    Allows chaining multiple filter and sort operations on task lists,
    reducing code duplication and improving readability. Each operation
    returns a new TaskQuery, enabling readable, chainable syntax.

    Example:
        results = (TaskQuery(scheduler.get_all_tasks())
                   .filter_by_pet(fluffy)
                   .filter_by_status('pending')
                   .sort_by('time')
                   .limit(5))

    Attributes:
        tasks (List[Task]): Current filtered/sorted task list
    """

    def __init__(self, tasks: List[Task]):
        """Initialize with a task list.

        Args:
            tasks: List of tasks to filter/sort
        """
        self.tasks = tasks

    def filter_by_pet(self, pet: Pet) -> 'TaskQuery':
        """Keep only tasks for a specific pet.

        Args:
            pet: The pet to filter by

        Returns:
            TaskQuery: New pipeline with pet-filtered tasks
        """
        return TaskQuery([t for t in self.tasks if t.pet == pet])

    def filter_by_status(self, status: str) -> 'TaskQuery':
        """Keep tasks by completion status.

        Args:
            status: Either 'pending' (incomplete) or 'done' (completed)

        Returns:
            TaskQuery: New pipeline with status-filtered tasks

        Raises:
            Status string is case-insensitive.
        """
        is_done = (status.lower() == 'done')
        return TaskQuery([t for t in self.tasks if t.is_completed == is_done])

    def filter_by_priority(self, priority: PriorityLevel) -> 'TaskQuery':
        """Keep only tasks with a specific priority level.

        Args:
            priority: PriorityLevel.HIGH, MEDIUM, or LOW

        Returns:
            TaskQuery: New pipeline with priority-filtered tasks
        """
        return TaskQuery([t for t in self.tasks if t.priority == priority])

    def sort_by(self, key: str) -> 'TaskQuery':
        """Sort by time or priority.

        Args:
            key: Sort key - either 'time' (chronological) or 'priority' (HIGH->MEDIUM->LOW)

        Returns:
            TaskQuery: New pipeline with sorted tasks

        Raises:
            ValueError: If key is neither 'time' nor 'priority'
        """
        if key.lower() == 'time':
            return TaskQuery(sort_by_time(self.tasks))
        elif key.lower() == 'priority':
            return TaskQuery(sorted(self.tasks, key=lambda t: PRIORITY_ORDER[t.priority]))
        else:
            raise ValueError(f"Unknown sort key: {key}")

    def limit(self, n: int) -> List[Task]:
        """Return only the first n tasks (terminal operation).

        Args:
            n: Maximum number of tasks to return

        Returns:
            List[Task]: First n tasks (or fewer if less than n exist)
        """
        return self.tasks[:n]

    def get_results(self) -> List[Task]:
        """Return all filtered/sorted tasks (terminal operation).

        Returns:
            List[Task]: All tasks in the current pipeline
        """
        return self.tasks


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
        return sorted(tasks, key=lambda t: PRIORITY_ORDER[t.priority])

    def get_tasks_sorted_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted chronologically by scheduled time (today first)."""
        if tasks is None:
            tasks = self.get_all_tasks()
        return sort_by_time(tasks)

    def get_overdue_tasks(self, current_time: datetime) -> List[Task]:
        """Return all incomplete tasks with scheduled times before or at the current time."""
        return [task for task in self.get_all_tasks() if task.time <= current_time and not task.is_completed]

    def get_upcoming_tasks(self, days_ahead: int = 7) -> List[Task]:
        """Get all tasks in the next N days, expanded from recurring patterns."""
        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)

        all_expanded = []
        for task in self.get_all_tasks():
            expanded = expand_recurring_task(task, days_ahead)
            all_expanded.extend(expanded)

        return [t for t in all_expanded if now <= t.time <= cutoff]

    def find_conflicts_for_owner(self, owner: Owner) -> List[Tuple[Task, Task]]:
        """Find all conflicting task pairs for an owner."""
        tasks = owner.get_tasks()
        return find_all_conflicts(tasks)

    def query_tasks(self, tasks: Optional[List[Task]] = None) -> TaskQuery:
        """Start a composable filter/sort pipeline."""
        if tasks is None:
            tasks = self.get_all_tasks()
        return TaskQuery(tasks)

    def mark_task_completed(self, task: Task) -> None:
        """Mark a task as completed."""
        task.mark_completed()
