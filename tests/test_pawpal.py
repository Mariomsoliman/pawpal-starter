from datetime import datetime
from pawpal_system import Owner, Pet, Scheduler, Task

def test_task_completion_and_pet_task_addition():
    pet, task = Pet("Mochi", "dog"), Task("Walk", datetime(2026, 10, 26, 8))
    pet.add_task(task); task.mark_complete()
    assert pet.list_tasks() == [task]
    assert pet.list_tasks(include_completed=False) == []
    assert task.completed is True

def test_scheduler_sorts_filters_recurrence_and_detects_conflicts():
    owner = Owner("Jordan"); dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog); owner.add_pet(cat)
    dog.add_task(Task("Walk", datetime(2026, 10, 19, 8), 30, recurrence="weekly"))
    cat.add_task(Task("Feed", datetime(2026, 10, 26, 8, 15), 10))
    scheduler = Scheduler(owner); schedule = scheduler.tasks_for_day(datetime(2026, 10, 26).date())
    assert [task.description for _, task in schedule] == ["Walk", "Feed"]
    assert [task.description for _, task in scheduler.filter_tasks(pet_name="Luna")] == ["Feed"]
    assert len(scheduler.find_conflicts(datetime(2026, 10, 26).date())) == 1
