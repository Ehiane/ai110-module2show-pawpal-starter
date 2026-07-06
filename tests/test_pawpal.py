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


class TestSortingCorrectness:
    """Test that tasks are sorted chronologically with today's tasks first"""

    def test_sort_by_time_returns_chronological_order(self):
        """Verify tasks are sorted chronologically (earliest first)"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        # Create tasks at different times
        now = datetime.now()
        task_morning = Task(
            description="Morning walk",
            time=now.replace(hour=8, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet
        )
        task_evening = Task(
            description="Evening walk",
            time=now.replace(hour=18, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet
        )
        task_afternoon = Task(
            description="Feeding",
            time=now.replace(hour=12, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=15,
            pet=pet
        )

        schedule = Schedule(pet=pet)
        # Add in non-chronological order (evening, morning, afternoon)
        schedule.add_task(task_evening)
        schedule.add_task(task_morning)
        schedule.add_task(task_afternoon)

        # Sort by time
        from pawpal_system import sort_by_time
        sorted_tasks = sort_by_time(schedule.tasks)

        assert sorted_tasks[0] == task_morning, "First task should be morning (8 AM)"
        assert sorted_tasks[1] == task_afternoon, "Second task should be afternoon (12 PM)"
        assert sorted_tasks[2] == task_evening, "Third task should be evening (6 PM)"

    def test_sort_by_priority_high_before_medium_before_low(self):
        """Verify tasks are sorted by priority (high → medium → low)"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        now = datetime.now()
        task_low = Task(
            description="Low priority task",
            time=now,
            priority=PriorityLevel.LOW,
            frequency=Frequency.ONCE,
            duration=10,
            pet=pet
        )
        task_high = Task(
            description="High priority task",
            time=now,
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=10,
            pet=pet
        )
        task_medium = Task(
            description="Medium priority task",
            time=now,
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=10,
            pet=pet
        )

        # Sort by priority using TaskQuery
        from pawpal_system import TaskQuery
        sorted_tasks = TaskQuery([task_low, task_medium, task_high]).sort_by('priority').get_results()

        assert sorted_tasks[0].priority == PriorityLevel.HIGH, "First should be HIGH priority"
        assert sorted_tasks[1].priority == PriorityLevel.MEDIUM, "Second should be MEDIUM priority"
        assert sorted_tasks[2].priority == PriorityLevel.LOW, "Third should be LOW priority"


class TestRecurrenceLogic:
    """Test that recurring tasks expand correctly"""

    def test_expand_daily_task_creates_instances(self):
        """Verify that a DAILY task expands to multiple instances"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        now = datetime.now()
        daily_task = Task(
            description="Daily feeding",
            time=now,
            priority=PriorityLevel.HIGH,
            frequency=Frequency.DAILY,
            duration=10,
            pet=pet
        )

        from pawpal_system import expand_recurring_task
        expanded = expand_recurring_task(daily_task, num_days=7)

        assert len(expanded) == 7, "DAILY task should expand to 7 instances over 7 days"
        assert all(t.description == "Daily feeding" for t in expanded), "All instances should have same description"
        assert expanded[0].time.date() < expanded[6].time.date(), "Last instance should be later than first"

    def test_expand_weekly_task_creates_weekly_instances(self):
        """Verify that a WEEKLY task expands correctly"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        now = datetime.now()
        weekly_task = Task(
            description="Weekly grooming",
            time=now,
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.WEEKLY,
            duration=60,
            pet=pet
        )

        from pawpal_system import expand_recurring_task
        expanded = expand_recurring_task(weekly_task, num_days=28)

        assert len(expanded) == 4, "WEEKLY task should expand to 4 instances over 28 days"
        assert (expanded[1].time.date() - expanded[0].time.date()).days == 7, "Weekly instances should be 7 days apart"

    def test_once_task_does_not_expand(self):
        """Verify that a ONCE task does not expand"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        now = datetime.now()
        once_task = Task(
            description="One-time task",
            time=now,
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet
        )

        from pawpal_system import expand_recurring_task
        expanded = expand_recurring_task(once_task, num_days=30)

        assert len(expanded) == 1, "ONCE task should not expand (only 1 instance)"
        assert expanded[0] == once_task, "The single instance should be the original task"


class TestConflictDetection:
    """Test that same-pet task conflicts are detected"""

    def test_same_time_conflict_detected(self):
        """Verify that two tasks for same pet at same time are flagged as conflict"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        now = datetime.now()
        task1 = Task(
            description="Playtime",
            time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=20,
            pet=pet
        )
        task2 = Task(
            description="Grooming",
            time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=15,
            pet=pet
        )

        from pawpal_system import has_conflict
        assert has_conflict(task1, task2) is True, "Same-time tasks for same pet should conflict"

    def test_overlapping_tasks_conflict(self):
        """Verify that overlapping tasks are detected as conflicts"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        now = datetime.now()
        task1 = Task(
            description="Task 1",
            time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=30,  # 3:00 PM - 3:30 PM
            pet=pet
        )
        task2 = Task(
            description="Task 2",
            time=now.replace(hour=15, minute=15, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=30,  # 3:15 PM - 3:45 PM (overlaps 15 mins)
            pet=pet
        )

        from pawpal_system import has_conflict
        assert has_conflict(task1, task2) is True, "Overlapping tasks for same pet should conflict"

    def test_no_conflict_for_different_pets(self):
        """Verify that same-time tasks for different pets do NOT conflict"""
        owner = Owner(name="Test Owner")
        pet1 = Pet(name="Pet 1", breed="Breed 1", age=1, owner=owner)
        pet2 = Pet(name="Pet 2", breed="Breed 2", age=2, owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        now = datetime.now()
        task1 = Task(
            description="Walk Pet 1",
            time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet1
        )
        task2 = Task(
            description="Walk Pet 2",
            time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet2
        )

        from pawpal_system import has_conflict
        assert has_conflict(task1, task2) is False, "Same-time tasks for different pets should NOT conflict"

    def test_adjacent_tasks_do_not_conflict(self):
        """Verify that adjacent tasks (one ends when other starts) do NOT conflict"""
        owner = Owner(name="Test Owner")
        pet = Pet(name="Test Pet", breed="Test Breed", age=1, owner=owner)
        owner.add_pet(pet)

        now = datetime.now()
        task1 = Task(
            description="Task 1",
            time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=20,  # 3:00 PM - 3:20 PM
            pet=pet
        )
        task2 = Task(
            description="Task 2",
            time=now.replace(hour=15, minute=20, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=20,  # 3:20 PM - 3:40 PM (starts exactly when task1 ends)
            pet=pet
        )

        from pawpal_system import has_conflict
        assert has_conflict(task1, task2) is False, "Adjacent tasks should NOT conflict"

    def test_find_all_conflicts_in_mixed_schedule(self):
        """Verify that find_all_conflicts correctly identifies all conflicts"""
        owner = Owner(name="Test Owner")
        pet1 = Pet(name="Fluffy", breed="Golden Retriever", age=3, owner=owner)
        pet2 = Pet(name="Whiskers", breed="Tabby Cat", age=2, owner=owner)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        now = datetime.now()

        # Fluffy tasks (no conflicts)
        fluffy_task1 = Task(
            description="Walk Fluffy",
            time=now.replace(hour=8, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=30,
            pet=pet1
        )
        fluffy_task2 = Task(
            description="Feed Fluffy",
            time=now.replace(hour=12, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=15,
            pet=pet1
        )

        # Whiskers tasks (2 conflicts)
        whiskers_task1 = Task(
            description="Playtime",
            time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=20,
            pet=pet2
        )
        whiskers_task2 = Task(
            description="Grooming",
            time=now.replace(hour=15, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=15,
            pet=pet2
        )
        whiskers_task3 = Task(
            description="Feeding",
            time=now.replace(hour=18, minute=0, second=0, microsecond=0),
            priority=PriorityLevel.HIGH,
            frequency=Frequency.ONCE,
            duration=10,
            pet=pet2
        )

        all_tasks = [fluffy_task1, fluffy_task2, whiskers_task1, whiskers_task2, whiskers_task3]

        from pawpal_system import find_all_conflicts
        conflicts = find_all_conflicts(all_tasks)

        assert len(conflicts) == 1, "Should find exactly 1 conflict (whiskers_task1 and whiskers_task2)"
        assert (whiskers_task1, whiskers_task2) in conflicts or (whiskers_task2, whiskers_task1) in conflicts, \
            "Conflict should be between the two Whiskers playtime/grooming tasks"
