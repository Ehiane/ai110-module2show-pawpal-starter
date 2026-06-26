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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
