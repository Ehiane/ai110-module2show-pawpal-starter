# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    The core design is centered 4 core classes, 
    Pets, Owners, Tasks, and Schedules.

- What classes did you include, and what responsibilities did you assign to each?
    * We need a Pet class, to identify the pet and it's attributes 
        * Attributes:
            * PetId: UUID
            * Name: string
            * Breed: string
            * Age: int
            * Owner: Owner
        * Methods:
            * Get_Owner()
            * Get_Name()
            * Get_Breed()
            * Get_Age()
            * Get_Owner()
    * We need an Owner class, to hold information about the pet it's related to and their preferences
        * Attributes:
            * OwnerId: UUID
            * Name: string
            * Pets: List[Pet]
            * Schedules: List[Schedule] //per pet
        * Methods:
            * Get_Pets()
            * Get_Tasks()
            * Get_OwnerID()
            * Get_Name()

    * we need a Task class, to collect information of what should be done to a pet, they could have priority as an attribute.
        * Attributes:
            * Time: DateTime
            * Priority: Enum(High, Medium, Low)
            * Owner_Preferences: Dict
            * Duration: int
        * Methods:
            * Get_TaskTime()
            * Get_PriorityLevel()
            * Get_OwnerPreferences()
            * Get_TaskDuration()

    * We need a Schedule class, which houses the collection of tasks needed to be done now and in the future. 
        * Attributes:
            * Tasks: List[Task]
        * Methods:
            * Get_Tasks()

**b. Design changes**

- Did your design change during implementation?
    * Yes
- If yes, describe at least one change and why you made it.
    * Having a Schedule class that determines the order of operations for tasks AKA priority. 
    They could be either done immediately or at a particular time.
    
    * **Additional refinement during code review:**
        * Added a `pet` field to Task class to establish which pet a task is for (previously unclear)
        * Added back-reference `schedule` in Task to enable finding which Schedule owns a task
        * Added filtering methods to Owner class: `get_tasks_by_priority()` and `get_tasks_for_pet()` to avoid inefficient loops throughout the codebase
        * Clarified that schedules are pet-specific rather than owner-level, improving the relationship model (each pet can have its own schedule)
    * **Why these changes were necessary:**
        * The original design had missing relationships—tasks didn't reference which pet they applied to, making the system ambiguous
        * The Owner.get_tasks() method was inefficient (O(n×m)) because it rebuilt the full task list on each call with no filtering capability
        * Without pet-specific queries, the scheduler couldn't efficiently answer "what tasks does Fluffy have?" or "what high-priority tasks need to be done?" 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  
  **Tradeoff: Per-Pet Conflict Detection vs. Owner-Level Availability**
  
  The scheduler detects conflicts *only within the same pet's tasks* (e.g., Fluffy can't have two walks at 3:00 PM). However, it does not detect *owner-level conflicts* where the owner is busy with one pet and cannot attend to another (e.g., owner walking Fluffy and grooming Whiskers simultaneously).
  
  **Implementation detail:** The `has_conflict(task1, task2)` function returns `False` immediately if the tasks are for different pets, without considering whether the owner is available to perform both tasks at once.

- Why is that tradeoff reasonable for this scenario?
  
  This tradeoff is reasonable because:
  1. **Multiple caretakers:** In a typical household, the owner may have family members, dog walkers, or pet sitters who can handle multiple pets simultaneously.
  2. **Different task types:** Some tasks (like feeding two pets) can be done quickly and sequentially, while others (like two walks) can't happen at the same time.
  3. **Complexity vs. benefit:** Detecting owner-level conflicts would require knowing the owner's availability, duration overlaps, and which tasks actually require active owner participation (feeding requires owner, but some pets can play independently).
  4. **User flexibility:** Displaying per-pet conflicts gives the owner immediate, actionable warnings about scheduling problems within each pet's schedule. Owner-level conflicts would require more complex UI and scheduling logic.
  
  **Future enhancement:** If the app needed to enforce owner-level availability, we could add a second check: `find_owner_level_conflicts()` that checks tasks for the same owner across all pets, with configurable task types that require active owner participation.

---

## 3. AI Collaboration

**a. How you used AI**

- **Code review & simplification:** Used AI to identify code duplication (module-level constants), unnecessary nesting (sort_by_time), and performance optimizations (pet-grouping in find_all_conflicts). The AI helped extract 5 high-impact improvements that reduced lines of code by 40-70%.
- **Test generation:** AI helped draft a comprehensive test suite covering sorting, recurrence, and conflict detection with both happy paths and edge cases. This ensured correctness before integration.
- **Documentation:** AI generated docstrings, README sections, and tradeoff explanations with the right level of technical detail, reducing documentation time significantly.

- **Most helpful prompts:**
  - "What are the high-impact simplifications you'd make to this code?" (led to concrete refactorings)
  - "Write tests for sorting, recurrence, and conflict detection with edge cases" (captured critical behaviors)
  - "Document one tradeoff your scheduler makes" (helped articulate design decisions)

**b. Judgment and verification**

- **One moment of disagreement:** AI initially suggested making Pet hashable by adding @dataclass(frozen=True). Instead, I chose to use `id(task.pet)` as the dict key in find_all_conflicts(), avoiding unnecessary changes to the Pet class. This was the right call because:
  - The Pet class mutation would have broader side effects
  - Using object identity as a key is a valid, Python-idiomatic solution
  - It keeps the class definition minimal
  
- **How I verified:** I ran the test suite (14 tests pass) and confirmed that find_all_conflicts() still correctly identifies all conflicts. Performance remains good.

---

## 4. Testing and Verification

**a. What you tested**

**Sorting Correctness:**
- Verified that tasks are returned in chronological order (earliest first)
- Verified that priority sorting works (HIGH → MEDIUM → LOW)
- Tested that today's tasks appear first (via (days_from_today, time_of_day) tuple)

**Recurring Task Expansion:**
- DAILY task over 7 days → 7 instances
- WEEKLY task over 28 days → 4 instances (7 days apart)
- ONCE task → stays as 1 instance (no expansion)

**Conflict Detection:**
- Same-time conflict: two tasks at exact same start time = conflict ✓
- Overlapping: Task A 3:00-3:30, Task B 3:15-3:45 = conflict ✓
- Different pets: Fluffy 3:00 PM, Whiskers 3:00 PM = NO conflict ✓
- Adjacent tasks: Task A 3:00-3:20, Task B 3:20-3:40 = NO conflict ✓
- Mixed schedule: found 1 conflict among 5 tasks (Whiskers playtime + grooming) ✓

**Why these tests matter:**
- Sorting ensures users see the most relevant (today's) tasks first
- Recurrence expansion is the heart of the scheduler's power (no need to manually enter daily tasks)
- Conflict detection prevents the app from suggesting impossible schedules

**b. Confidence**

- **Confidence level: 5/5 stars** — The scheduler works correctly. Here's why:
  - All 14 unit tests pass with 70% code coverage of core scheduling logic
  - Manual testing with main.py shows all features working end-to-end
  - Edge cases are explicitly tested (same-time, overlapping, adjacent, cross-pet)
  - The algorithm is simple and well-understood (no complex heuristics that could fail)

- **Edge cases I'd test next (if more time):**
  - Recurring task that expands to today AND past days (should handle gracefully)
  - Multiple owners with shared pets (conflict detection across ownership)
  - Task duration = 0 minutes (edge case for overlap calculation)
  - Scheduling 1000+ tasks (performance/scaling)
  - Daylight saving time edge cases (datetime transitions)

---

## 5. Reflection

**a. What went well**

- **Composable task filtering (TaskQuery):** The fluent API pattern for chaining filters (.filter_by_pet().filter_by_status().sort_by().limit()) is elegant and highly reusable. It reduced code duplication significantly and makes complex queries readable.
- **Lightweight conflict detection:** Rather than crashing or preventing task creation, the scheduler warns users and lets them decide. This balances safety with flexibility.
- **Code simplification:** Extracted module-level constants and encapsulated time calculations. The codebase is now 40% simpler in key areas without sacrificing clarity.

**b. What you would improve**

- **Owner-level availability:** Currently, the scheduler only detects per-pet conflicts. A future version could track owner availability across pets (e.g., owner can't walk Fluffy and groom Whiskers simultaneously).
- **UI/Streamlit integration:** The logic is solid, but the app still needs a user interface to make scheduling tasks and viewing the calendar interactive.
- **Batch operations:** Add methods like `reschedule_all_tasks()` or `duplicate_weekly_schedule()` to reduce manual effort for recurring patterns.
- **Conflict resolution suggestions:** When conflicts are detected, suggest alternatives (e.g., "Move grooming to 3:30 PM?").

**c. Key takeaway**

The most important thing I learned: **Simple, testable code beats clever code.** The scheduler's strength comes from:
1. Clear separation of concerns (Task, Schedule, Owner, Scheduler classes)
2. Small, focused functions that do one thing well (has_conflict, expand_recurring_task, find_all_conflicts)
3. Comprehensive tests that verify behavior, not implementation

Using AI to refactor and simplify made the code 10x easier to reason about and extend. The final version is something I'm proud to show and hand off.
