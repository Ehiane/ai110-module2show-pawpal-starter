import pytest
from datetime import datetime
from pawpal_system import Owner, Pet, Schedule, Task, PriorityLevel, Frequency


class TestTaskCompletion:
    """Test task completion functionality"""

    def test_mark_task_completed(self):
        """Verify that marking a task as completed changes its status"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        task = Task(
            description="Test task",
            time=datetime.now(),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet
        )

        assert task.is_task_completed() is False, "Task should not be completed initially"

        task.mark_completed()

        assert task.is_task_completed() is True, "Task should be completed after mark_completed()"

    def test_mark_task_incomplete(self):
        """Verify that marking a task as incomplete changes its status back to incomplete"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        task = Task(
            description="Test task",
            time=datetime.now(),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet,
            is_completed=True
        )

        assert task.is_task_completed() is True, "Task should be completed initially"

        task.mark_incomplete()

        assert task.is_task_completed() is False, "Task should be incomplete after mark_incomplete()"


class TestTaskAddition:
    """Test task addition to pets"""

    def test_add_task_to_schedule_increases_pet_task_count(self):
        """Verify that adding a task to a schedule increases the pet's task count"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        schedule = Schedule(pet=pet)
        owner.add_schedule(schedule)

        initial_task_count = len(pet.get_tasks())
        assert initial_task_count == 0, "Pet should have no tasks initially"

        task = Task(
            description="Test task",
            time=datetime.now(),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet
        )

        schedule.add_task(task)

        updated_task_count = len(pet.get_tasks())
        assert updated_task_count == 1, "Pet should have exactly 1 task after adding"
        assert pet.get_tasks()[0] == task, "The added task should be in the pet's task list"

    def test_add_multiple_tasks_increases_pet_task_count(self):
        """Verify that adding multiple tasks increases the pet's task count correctly"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        schedule = Schedule(pet=pet)
        owner.add_schedule(schedule)

        assert len(pet.get_tasks()) == 0, "Pet should have no tasks initially"

        task1 = Task(
            description="Task 1",
            time=datetime.now(),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet
        )

        task2 = Task(
            description="Task 2",
            time=datetime.now(),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.DAILY,
            duration=20,
            pet=pet
        )

        schedule.add_task(task1)
        assert len(pet.get_tasks()) == 1, "Pet should have 1 task after first addition"

        schedule.add_task(task2)
        assert len(pet.get_tasks()) == 2, "Pet should have 2 tasks after second addition"
