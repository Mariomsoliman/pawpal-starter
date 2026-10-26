"""Command-line demonstration of PawPal+ scheduling."""
from datetime import date, datetime
from pawpal_system import Owner, Pet, Scheduler, Task

def main() -> None:
    """Create a multi-pet schedule and print it."""
    today, owner = date.today(), Owner("Jordan")
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi); owner.add_pet(luna)
    mochi.add_task(Task("Morning walk", datetime.combine(today, datetime.strptime("08:00", "%H:%M").time()), 30, "high", recurrence="daily"))
    luna.add_task(Task("Breakfast", datetime.combine(today, datetime.strptime("08:15", "%H:%M").time()), 15, "high", recurrence="daily"))
    mochi.add_task(Task("Evening medication", datetime.combine(today, datetime.strptime("18:00", "%H:%M").time()), 5, "high"))
    scheduler = Scheduler(owner)
    print("Today's Schedule\n================")
    for pet, task in scheduler.tasks_for_day(today): print(f"{task.due_at:%H:%M} — {pet.name}: {task.description} ({task.duration_minutes} min, {task.priority})")
    for first, second in scheduler.find_conflicts(today): print(f"WARNING: {first[0].name}'s {first[1].description} overlaps {second[0].name}'s {second[1].description}.")
if __name__ == "__main__": main()
