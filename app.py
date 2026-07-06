import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Schedule, Task, PriorityLevel, Frequency, Scheduler

"""
PawPal+ Backend Integration Flow
=================================

Form Submission -> Backend Method Call -> Session State Update -> UI Rerun

ADD PET FLOW:
1. User fills: pet name, breed, age
2. Click "Add Pet" -> Pet constructor creates instance with owner reference
3. Owner.add_pet(pet) -> adds pet to owner's pets list (single source of truth)
4. Owner.add_schedule(schedule) -> validates pet belongs to owner, adds schedule
5. UI rerun -> pets list refreshes via st.session_state.owner.get_pets()

ADD TASK FLOW:
1. User selects pet from sidebar, fills: description, time, duration, priority, frequency
2. Click "Add Task" -> Task constructor creates instance with pet reference
3. Schedule.add_task(task) -> validates task.pet == schedule.pet (prevents cross-pet contamination)
4. Owner's schedules list updated -> accessible via st.session_state.owner.schedules
5. UI rerun -> Scheduler.get_all_tasks_for_owner() retrieves all tasks through Owner's schedules

KEY DESIGN PATTERNS:
- Owner is the gatekeeper: pets and schedules must go through Owner methods
- Schedule validates pet ownership at task addition time
- Task always has pet and schedule references (bidirectional integrity)
- UI queries through Scheduler layer for read operations (retrieval, sorting, filtering)
"""

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+, your pet care scheduling assistant.

Plan and manage care tasks for your pets with intelligent scheduling and priority management.
"""
)

# Initialize session state for owner, scheduler, and UI state
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
if "current_pet" not in st.session_state:
    st.session_state.current_pet = None

# Sidebar: Owner and Pet Management
with st.sidebar:
    st.header("Owner & Pet Setup")

    owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_input")

    if st.button("Create/Load Owner"):
        # Check if owner already exists in session state
        if st.session_state.owner is None:
            st.session_state.owner = Owner(name=owner_name)
            st.session_state.scheduler.add_owner(st.session_state.owner)
            st.success(f"Owner '{owner_name}' created!")
        else:
            st.info(f"Owner '{st.session_state.owner.get_name()}' already exists. Add pets or tasks.")

    if st.session_state.owner:
        st.divider()
        st.subheader("Pets")

        # Add new pet form
        with st.expander("Add a new pet"):
            pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
            pet_breed = st.text_input("Breed", value="Labrador", key="pet_breed_input")
            pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=2, key="pet_age_input")

            if st.button("Add Pet"):
                try:
                    # Owner.add_pet() is the single source of truth for pet creation
                    new_pet = Pet(name=pet_name, breed=pet_breed, age=pet_age, owner=st.session_state.owner)
                    st.session_state.owner.add_pet(new_pet)

                    # Owner.add_schedule() validates that the pet belongs to this owner
                    new_schedule = Schedule(pet=new_pet)
                    st.session_state.owner.add_schedule(new_schedule)

                    st.success(f"Pet '{pet_name}' added!")
                    st.rerun()
                except ValueError as ve:
                    st.error(f"Validation error: {ve}")
                except Exception as e:
                    st.error(f"Error adding pet: {e}")

        # Display existing pets
        pets = st.session_state.owner.get_pets()
        if pets:
            st.write("**Your Pets:**")
            for pet in pets:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    if st.button(f"📋 {pet.get_name()} ({pet.get_breed()})", key=f"pet_{pet.pet_id}"):
                        st.session_state.current_pet = pet
                with col2:
                    st.caption(f"{pet.get_age()} yo")
                with col3:
                    st.caption(f"{len(pet.get_tasks())} tasks")
        else:
            st.info("No pets yet. Add one above.")

# Main content area
if st.session_state.owner:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header(f"Schedule for {st.session_state.owner.get_name()}")
    with col2:
        if st.button("Refresh Schedule"):
            st.rerun()

    st.divider()

    # Task management section
    st.subheader("Add a Task")

    if st.session_state.current_pet:
        col1, col2, col3 = st.columns(3)

        with col1:
            task_desc = st.text_input("Task description", value="Morning walk", key="task_desc_input")

        with col2:
            task_time = st.time_input("Scheduled time", value=datetime.now().time(), key="task_time_input")

        with col3:
            task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30, key="task_duration_input")

        col1, col2, col3 = st.columns(3)

        with col1:
            task_priority = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"], key="task_priority_input")

        with col2:
            task_frequency = st.selectbox("Frequency", ["ONCE", "DAILY", "WEEKLY", "MONTHLY"], key="task_frequency_input")

        with col3:
            owner_notes = st.text_input("Owner notes (optional)", key="owner_notes_input")

        if st.button("Add Task"):
            try:
                task_time_dt = datetime.combine(datetime.now().date(), task_time)

                # Create task with the selected pet
                new_task = Task(
                    description=task_desc,
                    time=task_time_dt,
                    priority=PriorityLevel[task_priority],
                    frequency=Frequency[task_frequency],
                    duration=task_duration,
                    pet=st.session_state.current_pet,
                    owner_preferences={"notes": owner_notes} if owner_notes else {}
                )

                # Find the schedule for this pet using Owner's schedules list
                # Owner.add_schedule() validates ownership; Schedule.add_task() validates pet match
                pet_schedule = next(
                    (s for s in st.session_state.owner.schedules if s.get_pet() == st.session_state.current_pet),
                    None
                )

                if pet_schedule:
                    # Schedule.add_task() validates that task.pet matches schedule.pet
                    pet_schedule.add_task(new_task)
                    st.success(f"Task '{task_desc}' added for {st.session_state.current_pet.get_name()}!")
                    st.rerun()
                else:
                    st.error(f"No schedule found for {st.session_state.current_pet.get_name()}. This shouldn't happen.")
            except ValueError as ve:
                st.error(f"Validation error: {ve}")
            except Exception as e:
                st.error(f"Error adding task: {e}")
    else:
        st.info("Please select a pet from the sidebar to add tasks.")

    st.divider()

    # Display schedule
    st.subheader("Today's Schedule")

    all_tasks = st.session_state.scheduler.get_all_tasks_for_owner(st.session_state.owner)

    if all_tasks:
        # Check for conflicts and display warnings
        conflicts = st.session_state.scheduler.find_conflicts_for_owner(st.session_state.owner)
        if conflicts:
            st.warning(f"⚠️ **{len(conflicts)} scheduling conflict(s) detected!**")
            with st.expander("View conflicts"):
                for task1, task2 in conflicts:
                    overlap_start = max(task1.time, task2.time)
                    overlap_end = min(task1.get_end_time(), task2.get_end_time())
                    overlap_minutes = int((overlap_end - overlap_start).total_seconds() / 60)
                    st.write(
                        f"**{task1.pet.get_name()}** has conflicting tasks:\n"
                        f"- {task1.get_description()} @ {task1.time.strftime('%I:%M %p')} ({task1.duration} min)\n"
                        f"- {task2.get_description()} @ {task2.time.strftime('%I:%M %p')} ({task2.duration} min)\n"
                        f"Overlap: {overlap_minutes} minutes"
                    )
            st.divider()
        # Sort tasks by time
        sorted_tasks = st.session_state.scheduler.get_tasks_sorted_by_time(all_tasks)

        # Create a formatted table
        schedule_data = []
        for task in sorted_tasks:
            schedule_data.append({
                "Time": task.get_task_time().strftime("%I:%M %p"),
                "Pet": task.get_pet().get_name(),
                "Task": task.get_description(),
                "Duration": f"{task.get_task_duration()} min",
                "Priority": task.get_priority_level().value,
                "Status": "✓ Done" if task.is_task_completed() else "⏳ Pending"
            })

        st.dataframe(schedule_data, use_container_width=True)

        # Task management columns
        st.subheader("Manage Tasks")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Pending Tasks**")
            pending = st.session_state.scheduler.get_pending_tasks_for_owner(st.session_state.owner)
            if pending:
                for task in pending:
                    if st.button(f"✓ Mark done: {task.get_description()}", key=f"done_{task.task_id}"):
                        st.session_state.scheduler.mark_task_completed(task)
                        st.rerun()
            else:
                st.success("All tasks completed!")

        with col2:
            st.write("**Completed Tasks**")
            completed = st.session_state.scheduler.get_completed_tasks_for_owner(st.session_state.owner)
            if completed:
                for task in completed:
                    if st.button(f"↩ Mark pending: {task.get_description()}", key=f"pending_{task.task_id}"):
                        task.mark_incomplete()
                        st.rerun()
            else:
                st.info("No completed tasks yet.")

        st.divider()

        # Analytics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tasks", len(all_tasks))
        with col2:
            st.metric("Pending", len(pending))
        with col3:
            st.metric("Completed", len(completed))

        # Priority breakdown
        st.subheader("Tasks by Priority")
        high_priority = st.session_state.scheduler.get_tasks_by_priority_for_owner(st.session_state.owner, PriorityLevel.HIGH)
        medium_priority = st.session_state.scheduler.get_tasks_by_priority_for_owner(st.session_state.owner, PriorityLevel.MEDIUM)
        low_priority = st.session_state.scheduler.get_tasks_by_priority_for_owner(st.session_state.owner, PriorityLevel.LOW)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("High Priority", len(high_priority))
        with col2:
            st.metric("Medium Priority", len(medium_priority))
        with col3:
            st.metric("Low Priority", len(low_priority))

    else:
        st.info("No tasks yet. Add a pet and create some tasks to get started!")

else:
    st.warning("Please create an owner first using the sidebar to get started.")
