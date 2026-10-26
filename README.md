# PawPal+

PawPal+ is a small Streamlit pet-care planner for one owner and multiple pets. It stores care tasks with a time, duration, priority, completion state, and optional daily or weekly recurrence. The schedule is ordered by due time and warns when task windows overlap.

## Project structure

- `pawpal_system.py` contains the application model and scheduling rules.
- `main.py` is a reproducible command-line demonstration.
- `app.py` is the Streamlit interface.
- `diagrams/uml.mmd` is the Mermaid UML source.
- `tests/test_pawpal.py` covers the core behavior.

## Classes and algorithms

| Class | Responsibility |
|---|---|
| `Task` | Holds the description, due datetime, duration, priority, completion status, and recurrence. `mark_complete()` completes a task. |
| `Pet` | Holds identifying information and tasks. It can add and list tasks. |
| `Owner` | Manages multiple pets and returns all tasks paired with their pet. |
| `Scheduler` | Reads tasks through `Owner`, builds date-specific occurrences, sorts them, filters them, and finds overlaps. |

`Scheduler.tasks_for_day()` filters out completed tasks, expands daily or weekly tasks for the requested date, then sorts by `due_at`. `filter_tasks()` filters across all pets by pet name and/or completion state. `find_conflicts()` detects when a later task starts before an earlier task ends. The scheduler deliberately reports conflicts instead of silently moving tasks, so the owner can decide what should change.

## Persistence

The Streamlit app keeps the `Owner` object in `st.session_state`, so pets and tasks survive ordinary Streamlit reruns. **Save data** writes the current owner, pets, and tasks to `pawpal_data.json`; **Load saved data** rebuilds the object graph from that file. The JSON file is local data and is intentionally not committed by this project.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
streamlit run app.py
```

In the app, enter an owner name, add one or more pets, add timed tasks, then read **Today’s Schedule** and any conflict warnings. Choose daily or weekly in **Repeats** to make a task recur.

## CLI demo output

This is the real output from `python main.py`:

```text
Today's Schedule
================
08:00 — Mochi: Morning walk (30 min, high)
08:15 — Luna: Breakfast (15 min, high)
18:00 — Mochi: Evening medication (5 min, high)
WARNING: Mochi's Morning walk overlaps Luna's Breakfast.
```

## Tests

Run the full suite with exactly:

```bash
python -m pytest
```

Real output from the final run:

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/mariamsoliman/Pawpal starter /pawpal-starter
plugins: anyio-4.15.1
collected 2 items

tests/test_pawpal.py ..                                                  [100%]

============================== 2 passed in 0.01s ===============================
```

The tests cover task completion, pet task addition, sorting across pets, filtering by pet, weekly recurrence, and overlapping-task detection. Confidence is high for the tested core workflow; useful next tests would cover JSON round-tripping, same-start-time tasks, and a recurrence start date in the future.
