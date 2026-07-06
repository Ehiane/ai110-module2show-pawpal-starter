from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Schedule, Task, PriorityLevel, Frequency, Scheduler


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

    # Get today's date and create tasks at different times
    today = datetime.now()

    # Task 1: Fluffy - Morning walk (8:00 AM)
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

    # Task 2: Fluffy - Feeding (12:00 PM)
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

    # Task 3: Whiskers - Feeding (9:00 AM)
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

    # Task 4: Whiskers - Playtime (3:00 PM)
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

    # Task 5: Fluffy - Evening walk (6:00 PM)
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

    # Task 6: Whiskers - Litter box maintenance (5:00 PM)
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

    # Display upcoming tasks
    upcoming = [t for t in all_tasks if t.get_task_time() > datetime.now()]
    print("+" + "-" * 78 + "+")
    print("|" + " UPCOMING TASKS ".center(78) + "|")
    print("+" + "-" * 78 + "+")
    if upcoming:
        for task in sorted(upcoming, key=lambda t: t.get_task_time())[:5]:
            time_str = task.get_task_time().strftime("%I:%M %p")
            print(f"| > {time_str} - {task.get_pet().get_name()}: {task.get_description():<46} |")
    else:
        print("|" + " No upcoming tasks for today!".center(78) + "|")
    print("+" + "-" * 78 + "+\n")


if __name__ == "__main__":
    main()
