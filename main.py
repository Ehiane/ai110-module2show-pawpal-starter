from datetime import datetime, timedelta
from typing import List
from pawpal_system import (
    Owner, Pet, Schedule, Task, PriorityLevel, Frequency, Scheduler,
    has_conflict, expand_recurring_task, find_all_conflicts, sort_by_time, TaskQuery
)


def print_schedule_header():
    """Print ASCII art header for today's schedule"""
    print("\n" + "=" * 80)
    print("""
    +===============================================================+
    |                   TODAY'S PET SCHEDULE                         |
    +===============================================================+
    """)
    print("=" * 80 + "\n")


def format_task_row(time_str: str, pet_name: str, description: str, priority: str, duration: str):
    """Format a task row for the schedule table"""
    time_cell = f" {time_str:<12} "
    pet_cell = f" {pet_name:<17} "
    desc_cell = f" {description:<28} "
    priority_cell = f" {priority:<10} "
    duration_cell = f" {duration:<8} "

    return f"|{time_cell}|{pet_cell}|{desc_cell}|{priority_cell}|{duration_cell}|"


def print_schedule_table(tasks: list):
    """Print formatted schedule table with ASCII borders"""
    # Table header
    print("+----------------+---------------------+------------------------------+------------+----------+")
    print("|     TIME       |    PET NAME         |      TASK DESCRIPTION        |  PRIORITY  | DURATION |")
    print("+----------------+---------------------+------------------------------+------------+----------+")

    # Sort tasks by time
    sorted_tasks = sorted(tasks, key=lambda t: t.get_task_time())

    for task in sorted_tasks:
        time_str = task.get_task_time().strftime("%I:%M %p")
        pet_name = task.get_pet().get_name()
        description = task.get_description()[:28]
        priority = task.get_priority_level().value
        duration = f"{task.get_task_duration()} min"

        status = "[X]" if task.is_task_completed() else "[ ]"
        print(format_task_row(time_str, pet_name, description, priority, duration))

    print("+----------------+---------------------+------------------------------+------------+----------+\n")


def print_pet_summary(owner: Owner):
    """Print a summary of each pet and their task count"""
    print("+" + "-" * 78 + "+")
    print("|" + " PET SUMMARY ".center(78) + "|")
    print("+" + "-" * 78 + "+")

    for pet in owner.get_pets():
        tasks = pet.get_tasks()
        pending = pet.get_pending_tasks()
        completed = pet.get_completed_tasks()

        summary_text = f"* {pet.get_name()} ({pet.get_breed()}, {pet.get_age()} years old)"
        status_text = f"Pending: {len(pending)} | Completed: {len(completed)} | Total: {len(tasks)}"

        print(f"| {summary_text:<38} {status_text:>38} |")

    print("+" + "-" * 78 + "+\n")


def print_expanded_recurring_tasks(scheduler: Scheduler, owner: Owner, days: int = 7):
    """Demonstrate recurring task expansion (Improvement #1)."""
    print("\n" + "=" * 80)
    print("""
    +===============================================================+
    |           RECURRING TASKS EXPANDED (7 Days)                   |
    +===============================================================+
    """)
    print("=" * 80 + "\n")

    recurring_tasks = [t for t in scheduler.get_all_tasks_for_owner(owner) if t.frequency != Frequency.ONCE]
    if not recurring_tasks:
        print("No recurring tasks found.\n")
        return

    expanded = []
    for task in recurring_tasks:
        expanded.extend(expand_recurring_task(task, days))

    expanded_sorted = sort_by_time(expanded)

    print(f"Original recurring tasks: {len(recurring_tasks)}")
    print(f"Expanded to {len(expanded_sorted)} instances over {days} days\n")

    print("+----------------+---------------------+------------------------------+------------+----------+")
    print("|     TIME       |    PET NAME         |      TASK DESCRIPTION        |  PRIORITY  | FREQUENCY|")
    print("+----------------+---------------------+------------------------------+------------+----------+")

    for task in expanded_sorted:
        time_str = task.time.strftime("%a %I:%M %p")
        pet_name = task.pet.get_name()
        description = task.description[:28]
        priority = task.priority.value
        frequency = task.frequency.value

        print(f"| {time_str:<14} | {pet_name:<19} | {description:<28} | {priority:<10} | {frequency:<8} |")

    print("+----------------+---------------------+------------------------------+------------+----------+\n")


def print_conflict_detection(scheduler: Scheduler, owner: Owner):
    """Demonstrate conflict detection (Improvement #2)."""
    print("\n" + "=" * 80)
    print("""
    +===============================================================+
    |              CONFLICT DETECTION REPORT                        |
    +===============================================================+
    """)
    print("=" * 80 + "\n")

    conflicts = scheduler.find_conflicts_for_owner(owner)

    if not conflicts:
        print("[OK] No scheduling conflicts found! Schedule is feasible.\n")
    else:
        print(f"[WARNING] {len(conflicts)} conflict(s) detected - corrective action needed:\n")
        for i, (task1, task2) in enumerate(conflicts, 1):
            time1 = task1.time.strftime('%I:%M %p')
            time2 = task2.time.strftime('%I:%M %p')
            same_time = (task1.time == task2.time)

            print(f"  {i}. {task1.pet.get_name().upper()} - Schedule Conflict")
            print(f"     Task A: {task1.description}")
            print(f"             @ {time1} ({task1.duration} min)")
            print(f"     Task B: {task2.description}")
            print(f"             @ {time2} ({task2.duration} min)")

            if same_time:
                print(f"     [CRITICAL] Both tasks scheduled at EXACT SAME TIME!")
                overlap_mins = min(task1.duration, task2.duration)
                print(f"     Overlap: {overlap_mins} minutes minimum")
            else:
                end1 = task1.time + timedelta(minutes=task1.duration)
                start2 = task2.time
                overlap_start = max(task1.time, task2.time)
                overlap_end = min(end1, task2.time + timedelta(minutes=task2.duration))
                overlap_mins = max(0, (overlap_end - overlap_start).total_seconds() / 60)
                print(f"     Overlap: {int(overlap_mins)} minutes")
            print()


def print_out_of_order_verification(all_tasks: List[Task]):
    """Verify that sorting/filtering works on out-of-order input (Improvement Test)."""
    print("\n" + "=" * 80)
    print("""
    +===============================================================+
    |    VERIFICATION: SORTING & FILTERING ON OUT-OF-ORDER INPUT    |
    +===============================================================+
    """)
    print("=" * 80 + "\n")

    print("STEP 1: Original task insertion order (out of sequence)")
    print("-" * 80)
    for i, task in enumerate(all_tasks, 1):
        time_str = task.time.strftime("%I:%M %p")
        status = "[X] Done" if task.is_completed else "[ ] Pending"
        print(f"  {i}. {time_str} - {task.pet.name}: {task.description:<30} | {status}")
    print()

    print("STEP 2: Sorted by time (using sort_by_time())")
    print("-" * 80)
    sorted_by_time = sort_by_time(all_tasks)
    for i, task in enumerate(sorted_by_time, 1):
        time_str = task.time.strftime("%I:%M %p")
        status = "[X] Done" if task.is_completed else "[ ] Pending"
        print(f"  {i}. {time_str} - {task.pet.name}: {task.description:<30} | {status}")
    print()

    print("STEP 3: Filtered by status='pending' (incomplete tasks only)")
    print("-" * 80)
    pending = (TaskQuery(all_tasks)
               .filter_by_status('pending')
               .get_results())
    for i, task in enumerate(pending, 1):
        time_str = task.time.strftime("%I:%M %p")
        print(f"  {i}. {time_str} - {task.pet.name}: {task.description:<30}")
    print()

    print("STEP 4: Filtered by status='done' (completed tasks only)")
    print("-" * 80)
    done = (TaskQuery(all_tasks)
            .filter_by_status('done')
            .get_results())
    for i, task in enumerate(done, 1):
        time_str = task.time.strftime("%I:%M %p")
        print(f"  {i}. {time_str} - {task.pet.name}: {task.description:<30}")
    print()

    print("STEP 5: Combined - pending tasks sorted by time")
    print("-" * 80)
    combined = (TaskQuery(all_tasks)
                .filter_by_status('pending')
                .sort_by('time')
                .get_results())
    for i, task in enumerate(combined, 1):
        time_str = task.time.strftime("%I:%M %p")
        print(f"  {i}. {time_str} - {task.pet.name}: {task.description:<30}")
    print()


def print_composable_filters(scheduler: Scheduler, owner: Owner):
    """Demonstrate composable filtering/sorting pipeline (Improvement #3)."""
    print("\n" + "=" * 80)
    print("""
    +===============================================================+
    |         COMPOSABLE FILTER/SORT EXAMPLES                       |
    +===============================================================+
    """)
    print("=" * 80 + "\n")

    all_tasks = scheduler.get_all_tasks_for_owner(owner)
    fluffy = owner.get_pets()[0] if owner.get_pets() else None

    if fluffy:
        print("Example 1: All pending tasks for Fluffy, sorted by time")
        result1 = (scheduler.query_tasks(all_tasks)
                   .filter_by_pet(fluffy)
                   .filter_by_status('pending')
                   .sort_by('time')
                   .get_results())

        for task in result1:
            print(f"  • {task.time.strftime('%I:%M %p')} - {task.description} ({task.priority.value})")
        print()

    print("Example 2: All high-priority tasks, sorted by time")
    result2 = (scheduler.query_tasks(all_tasks)
               .filter_by_priority(PriorityLevel.HIGH)
               .sort_by('time')
               .get_results())

    for task in result2:
        print(f"  • {task.time.strftime('%I:%M %p')} - {task.pet.get_name()}: {task.description}")
    print()

    print("Example 3: First 3 upcoming pending tasks")
    result3 = (scheduler.query_tasks(all_tasks)
               .filter_by_status('pending')
               .sort_by('time')
               .limit(3))

    for task in result3:
        print(f"  • {task.time.strftime('%I:%M %p')} - {task.pet.get_name()}: {task.description}")
    print()


def main():
    # Create an owner
    owner = Owner(name="Alice Johnson")

    # Create two pets
    fluffy = Pet(name="Fluffy", breed="Golden Retriever", age=3, owner=owner)
    whiskers = Pet(name="Whiskers", breed="Tabby Cat", age=2, owner=owner)

    # Add pets to owner
    owner.add_pet(fluffy)
    owner.add_pet(whiskers)

    # Create schedules for each pet
    fluffy_schedule = Schedule(pet=fluffy)
    whiskers_schedule = Schedule(pet=whiskers)

    # Add schedules to owner
    owner.add_schedule(fluffy_schedule)
    owner.add_schedule(whiskers_schedule)

    # Get today's date and create tasks at DIFFERENT TIMES (not in order)
    today = datetime.now()

    # Task 5: Fluffy - Evening walk (6:00 PM) - ADDED FIRST (out of order)
    evening_walk = Task(
        description="Evening walk and bathroom break",
        time=today.replace(hour=18, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.HIGH,
        frequency=Frequency.DAILY,
        duration=30,
        pet=fluffy,
        owner_preferences={"route": "Neighborhood loop", "with_leash": True}
    )
    fluffy_schedule.add_task(evening_walk)

    # Task 3: Whiskers - Feeding (9:00 AM) - ADDED SECOND
    cat_breakfast = Task(
        description="Breakfast meal",
        time=today.replace(hour=9, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.HIGH,
        frequency=Frequency.DAILY,
        duration=10,
        pet=whiskers,
        owner_preferences={"food_type": "wet food", "amount": "1 can"}
    )
    whiskers_schedule.add_task(cat_breakfast)

    # Task 1: Fluffy - Morning walk (8:00 AM) - ADDED THIRD
    morning_walk = Task(
        description="Morning walk in the park",
        time=today.replace(hour=8, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.HIGH,
        frequency=Frequency.DAILY,
        duration=30,
        pet=fluffy,
        owner_preferences={"route": "Central Park", "with_leash": True}
    )
    fluffy_schedule.add_task(morning_walk)

    # Task 6: Whiskers - Litter box maintenance (5:00 PM) - ADDED FOURTH
    litter_clean = Task(
        description="Clean litter box",
        time=today.replace(hour=17, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.MEDIUM,
        frequency=Frequency.DAILY,
        duration=10,
        pet=whiskers,
        owner_preferences={"type": "scoop and refresh"}
    )
    whiskers_schedule.add_task(litter_clean)

    # Task 2: Fluffy - Feeding (12:00 PM) - ADDED FIFTH
    lunch_feed = Task(
        description="Lunch feeding",
        time=today.replace(hour=12, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.HIGH,
        frequency=Frequency.DAILY,
        duration=15,
        pet=fluffy,
        owner_preferences={"food_type": "dry kibble", "amount": "2 cups"}
    )
    fluffy_schedule.add_task(lunch_feed)

    # Task 4: Whiskers - Playtime (3:00 PM) - ADDED SIXTH
    playtime = Task(
        description="Interactive playtime",
        time=today.replace(hour=15, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.MEDIUM,
        frequency=Frequency.DAILY,
        duration=20,
        pet=whiskers,
        owner_preferences={"toys": ["feather wand", "laser pointer"]}
    )
    whiskers_schedule.add_task(playtime)

    # Task 7: Whiskers - Grooming (3:00 PM - SAME TIME as Playtime!) - CONFLICT TEST
    grooming = Task(
        description="Quick grooming session",
        time=today.replace(hour=15, minute=0, second=0, microsecond=0),
        priority=PriorityLevel.MEDIUM,
        frequency=Frequency.DAILY,
        duration=15,
        pet=whiskers,
        owner_preferences={"tools": ["brush", "nail clippers"]}
    )
    whiskers_schedule.add_task(grooming)

    # Mark some tasks as completed for demo
    morning_walk.mark_completed()
    cat_breakfast.mark_completed()

    # Create scheduler and add owner
    scheduler = Scheduler()
    scheduler.add_owner(owner)

    # Display the schedule
    print_schedule_header()

    # Get all tasks for today and display
    all_tasks = scheduler.get_all_tasks_for_owner(owner)
    print_schedule_table(all_tasks)

    # Display pet summary
    print_pet_summary(owner)

    # VERIFICATION: Test sorting & filtering on out-of-order input
    print_out_of_order_verification(all_tasks)

    # IMPROVEMENT #1: Recurring Task Expansion
    print_expanded_recurring_tasks(scheduler, owner, days=7)

    # IMPROVEMENT #2: Conflict Detection
    print_conflict_detection(scheduler, owner)

    # IMPROVEMENT #3: Composable Filters/Sorting
    print_composable_filters(scheduler, owner)

    # Display overdue tasks
    print("+" + "-" * 78 + "+")
    print("|" + " OVERDUE TASKS ".center(78) + "|")
    print("+" + "-" * 78 + "+")
    overdue = scheduler.get_overdue_tasks(datetime.now())
    if overdue:
        for task in overdue:
            status = "[X]" if task.is_task_completed() else "[!]"
            print(f"| {status} {task.get_pet().get_name()}: {task.get_description():<66} |")
    else:
        print("|" + " No overdue tasks! All set!".center(78) + "|")
    print("+" + "-" * 78 + "+\n")

    # Display upcoming tasks (using new sort_by_time function)
    upcoming = [t for t in all_tasks if t.get_task_time() > datetime.now()]
    print("+" + "-" * 78 + "+")
    print("|" + " UPCOMING TASKS ".center(78) + "|")
    print("+" + "-" * 78 + "+")
    if upcoming:
        for task in sort_by_time(upcoming)[:5]:
            time_str = task.get_task_time().strftime("%I:%M %p")
            print(f"| > {time_str} - {task.get_pet().get_name()}: {task.get_description():<46} |")
    else:
        print("|" + " No upcoming tasks for today!".center(78) + "|")
    print("+" + "-" * 78 + "+\n")


if __name__ == "__main__":
    main()
