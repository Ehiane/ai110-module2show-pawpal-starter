"""
Demo script: Conflict Detection in Action

This script shows what happens when you try to schedule two overlapping tasks
for the same pet. It demonstrates the has_conflict() and find_all_conflicts()
algorithms in a realistic scenario.
"""

from datetime import datetime, timedelta
from pawpal_system import (
    Owner, Pet, Schedule, Task, PriorityLevel, Frequency, Scheduler,
    has_conflict, find_all_conflicts, sort_by_time
)


def main():
    print("\n" + "=" * 80)
    print("""
    +===============================================================+
    |         CONFLICT DETECTION DEMO - Overlapping Tasks           |
    +===============================================================+
    """)
    print("=" * 80 + "\n")

    # Setup
    owner = Owner(name="Bob Smith")
    fluffy = Pet(name="Fluffy", breed="Golden Retriever", age=3, owner=owner)
    owner.add_pet(fluffy)
    fluffy_schedule = Schedule(pet=fluffy)
    owner.add_schedule(fluffy_schedule)

    today = datetime.now()

    # Create tasks that DON'T conflict
    print("Scenario 1: NON-CONFLICTING SCHEDULE")
    print("-" * 80)

    task1 = Task(
        description="Morning walk",
        time=today.replace(hour=8, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.HIGH,
        frequency=Frequency.ONCE,
        duration=30,
        pet=fluffy
    )

    task2 = Task(
        description="Lunch feeding",
        time=today.replace(hour=12, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.HIGH,
        frequency=Frequency.ONCE,
        duration=15,
        pet=fluffy
    )

    fluffy_schedule.add_task(task1)
    fluffy_schedule.add_task(task2)

    print(f"Task 1: {task1.description}")
    print(f"  Time: {task1.time.strftime('%I:%M %p')} - {(task1.time + timedelta(minutes=task1.duration)).strftime('%I:%M %p')} ({task1.duration} min)")
    print(f"\nTask 2: {task2.description}")
    print(f"  Time: {task2.time.strftime('%I:%M %p')} - {(task2.time + timedelta(minutes=task2.duration)).strftime('%I:%M %p')} ({task2.duration} min)")

    has_conflict_result = has_conflict(task1, task2)
    print(f"\nConflict check: {has_conflict_result}")
    print(f"Result: {'CONFLICT DETECTED!' if has_conflict_result else 'No conflict - schedule is OK'}\n")

    # Now create a CONFLICTING schedule
    print("\n" + "=" * 80)
    print("\nScenario 2: CONFLICTING SCHEDULE")
    print("-" * 80)

    owner2 = Owner(name="Alice White")
    whiskers = Pet(name="Whiskers", breed="Tabby Cat", age=2, owner=owner2)
    owner2.add_pet(whiskers)
    whiskers_schedule = Schedule(pet=whiskers)
    owner2.add_schedule(whiskers_schedule)

    task3 = Task(
        description="Playtime session",
        time=today.replace(hour=15, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.MEDIUM,
        frequency=Frequency.ONCE,
        duration=30,
        pet=whiskers
    )

    task4 = Task(
        description="Feeding time",
        time=today.replace(hour=15, minute=15, second=0, microsecond=0),
        priority=PriorityLevel.HIGH,
        frequency=Frequency.ONCE,
        duration=20,
        pet=whiskers
    )

    whiskers_schedule.add_task(task3)
    whiskers_schedule.add_task(task4)

    print(f"Task 3: {task3.description}")
    print(f"  Time: {task3.time.strftime('%I:%M %p')} - {(task3.time + timedelta(minutes=task3.duration)).strftime('%I:%M %p')} ({task3.duration} min)")
    print(f"\nTask 4: {task4.description}")
    print(f"  Time: {task4.time.strftime('%I:%M %p')} - {(task4.time + timedelta(minutes=task4.duration)).strftime('%I:%M %p')} ({task4.duration} min)")

    has_conflict_result = has_conflict(task3, task4)
    print(f"\nConflict check: {has_conflict_result}")
    print(f"Result: {'CONFLICT DETECTED!' if has_conflict_result else 'No conflict - schedule is OK'}")
    print(f"\nOverlap window: 3:15 PM - 3:30 PM (15 minutes)\n")

    # Batch conflict detection
    print("\n" + "=" * 80)
    print("\nScenario 3: BATCH CONFLICT DETECTION")
    print("-" * 80)

    owner3 = Owner(name="Charlie Brown")
    max_pet = Pet(name="Max", breed="Labrador", age=5, owner=owner3)
    owner3.add_pet(max_pet)
    max_schedule = Schedule(pet=max_pet)
    owner3.add_schedule(max_schedule)

    # Create 5 tasks with some conflicts
    times = [
        (8, 0, 30),   # 8:00-8:30
        (8, 15, 20),  # 8:15-8:35 - CONFLICT with task 1
        (9, 0, 30),   # 9:00-9:30
        (9, 25, 30),  # 9:25-9:55 - CONFLICT with task 3
        (10, 0, 30),  # 10:00-10:30 - no conflict
    ]

    tasks = []
    for i, (hour, minute, duration) in enumerate(times):
        task = Task(
            description=f"Activity {i+1}",
            time=today.replace(hour=hour, minute=minute, second=0, microsecond=0),
            priority=PriorityLevel.HIGH if i % 2 == 0 else PriorityLevel.MEDIUM,
            frequency=Frequency.ONCE,
            duration=duration,
            pet=max_pet
        )
        tasks.append(task)
        max_schedule.add_task(task)

    print(f"Created {len(tasks)} tasks:")
    for i, task in enumerate(tasks):
        end_time = task.time + timedelta(minutes=task.duration)
        print(f"  {i+1}. {task.time.strftime('%I:%M %p')}-{end_time.strftime('%I:%M %p')} ({task.duration} min) - {task.description}")

    conflicts = find_all_conflicts(tasks)
    print(f"\nBatch conflict detection results:")
    if conflicts:
        print(f"[ALERT] Found {len(conflicts)} conflict(s):\n")
        for i, (t1, t2) in enumerate(conflicts, 1):
            overlap_start = max(t1.time, t2.time)
            overlap_end = min(
                t1.time + timedelta(minutes=t1.duration),
                t2.time + timedelta(minutes=t2.duration)
            )
            overlap_mins = int((overlap_end - overlap_start).total_seconds() / 60)

            print(f"  Conflict {i}:")
            print(f"    - '{t1.description}' @ {t1.time.strftime('%I:%M %p')} ({t1.duration} min)")
            print(f"    - '{t2.description}' @ {t2.time.strftime('%I:%M %p')} ({t2.duration} min)")
            print(f"    - Overlaps: {overlap_start.strftime('%I:%M %p')}-{overlap_end.strftime('%I:%M %p')} ({overlap_mins} min)\n")
    else:
        print("[OK] No conflicts found!")

    print("\n" + "=" * 80)
    print("Conflict detection demo completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
