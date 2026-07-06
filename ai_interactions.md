# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked Claude to help with the code simplification phase (Phase 5). Specifically, I wanted to identify high-impact refactoring opportunities in the scheduling logic—places where the code had duplication, unnecessary nesting, or could be optimized without breaking functionality. I provided the full pawpal_system.py file and asked it to suggest 5 concrete improvements.

**What did the agent do?**

The agent reviewed the code and identified these specific changes:
1. Extracted `PRIORITY_ORDER` and `FREQUENCY_STEP` to module-level constants (was hardcoded in 2+ places each)
2. Added `Task.get_end_time()` method to encapsulate the time calculation logic
3. Simplified `sort_by_time()` by replacing a nested function with a lambda (10 lines → 3 lines)
4. Optimized `find_all_conflicts()` by grouping tasks by pet first before comparing (avoided ~50% of unnecessary cross-pet comparisons)
5. Streamlined `has_conflict()` by combining two conditional checks into one line

The agent then:
- Applied all 5 changes to the code
- Ran the test suite to verify nothing broke
- Generated a detailed SIMPLIFICATION_REVIEW.md documenting each change with before/after code
- Committed the changes with a comprehensive commit message

**What did you have to verify or fix manually?**

I had to fix one issue: the agent initially tried to make Pet hashable by adding `@dataclass(frozen=True)`, which would have been a breaking change. Instead, I kept the original Pet class and had the agent use `id(task.pet)` as a dictionary key in find_all_conflicts(). This was better because:
- Preserves the original class design
- Still achieves the optimization we needed
- Doesn't force immutability on a dataclass that didn't need it

I also manually reviewed each simplification to ensure the logic was still correct, especially the conflict detection optimization. Ran main.py to verify the schedule still showed correctly and conflicts were still detected.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Haiku (faster, cheaper) | Claude Opus (more capable, slower) |
| **Prompt** | "Write tests for sorting, recurrence, and conflict detection with edge cases" | Same prompt with more context about expected behavior |
| **Response summary** | Generated 14 unit tests covering happy paths and edge cases in ~1 minute. All tests passed on first run. | Would have generated similar tests but with more explanation and edge case discussion upfront. |
| **What was useful** | Haiku was fast enough to iterate on. The tests it generated were comprehensive and correct. No need to wait for a slower model. | More detailed reasoning would have been nice for understanding the test design, but not necessary since I could verify correctness by running the tests. |
| **Problems noticed** | Had to manually fix test function signatures (e.g., `days=7` vs `num_days=7`) when they didn't match the actual function signatures. Not a major issue—just needed to check the implementation first. | Would have been slower, which doesn't matter much for a one-time task. |
| **Decision** | Used Haiku for all test generation and most code work. Fast iteration was valuable when testing multiple approaches. | Reserved Opus-level thinking for design decisions (architecture choices, tradeoff analysis) where deeper reasoning provided real value. |

**Which approach did you use in your final implementation and why?**

I used Claude Haiku for the bulk of the work—test generation, code review, refactoring suggestions, documentation—because speed of iteration mattered more than raw capability for these tasks. For the 14 unit tests, I could verify correctness immediately by running them, so Haiku's response was sufficient and I got feedback faster.

For bigger picture decisions (like whether to implement per-pet vs. owner-level conflict detection, or how to structure the TaskQuery API), I used more careful reasoning to think through tradeoffs. This two-tier approach—fast AI for implementation details, deliberate thinking for architecture—ended up being the sweet spot. I avoided getting blocked on model choice and focused on what actually mattered: correctness and design quality.
