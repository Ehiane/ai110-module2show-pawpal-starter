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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
