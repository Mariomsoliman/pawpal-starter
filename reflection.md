# PawPal+ Project Reflection

## 1. System Design

### Initial design

I used four classes: `Task` for a timed care item, `Pet` for its identifying data and task list, `Owner` for the collection of pets, and `Scheduler` for cross-pet scheduling. The UML source in `diagrams/uml.mmd` records those relationships.

### Design changes

The starter had no backend classes. During implementation I added `due_at` as one datetime rather than separate date and time fields, because sorting and overlap checks both need a comparable timestamp. I also added `recurrence` to `Task` and create a dated occurrence when a schedule is requested, which avoids storing a separate copy of a daily task for every date.

## 2. Scheduling Logic and Tradeoffs

### Constraints and priorities

The scheduler uses due time, task duration, completion state, pet name, and recurrence. It sorts by due time and shows priority in the output; priority is stored for the owner’s decision rather than used to reorder a task past its selected time.

### Tradeoffs

When two tasks overlap, the app reports a warning instead of automatically moving one. That is reasonable here because automatic changes could make a medication or feeding task late without the owner noticing.

## 3. AI Collaboration

### How I used AI

I have used it to structure my mplementation plan and the command-based verification.

### Judgment and verification

I  used `python main.py`, `python -m pytest`, compilation, and imports to check the code. I also chose conflict warnings rather than an unrequested auto-rescheduling rule.

## 4. Testing and Verification

### What I tested

The tests confirm that a pet receives a task, `mark_complete()` changes its state, completed tasks can be omitted, cross-pet tasks are time-sorted, filtering finds a requested pet’s tasks, weekly recurrence creates an occurrence on the matching weekday, and overlap detection finds a conflict.

### Confidence

I have high confidence in the tested workflow because the final test run passed and the CLI demo printed the expected ordered schedule and warning. I would next test JSON save/load, same-time task boundaries, invalid inputs, and dates before a recurring task begins.

## 5. Reflection

### What went well

The project now has one consistent model shared by the CLI, tests, and Streamlit UI, rather than separate implementations of the same rules.

### What I would improve

A future iteration could let owners mark a task complete in the UI, edit or delete tasks, choose the displayed date, and add an explicit availability window.

### Key takeaway

Keeping schedule logic in a small tested module made it possible to reuse the same behavior in the command-line demo and the UI.

