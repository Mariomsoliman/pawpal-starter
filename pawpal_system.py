"""Domain model, scheduling helpers, and JSON persistence for PawPal+."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal

Recurrence = Literal["none", "daily", "weekly"]

@dataclass
class Task:
    """A single pet-care task with a scheduled start."""
    description: str
    due_at: datetime
    duration_minutes: int = 30
    priority: str = "medium"
    completed: bool = False
    recurrence: Recurrence = "none"
    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True
    def occurs_on(self, target_date: date) -> bool:
        """Return whether this task happens on the selected day."""
        if self.recurrence == "daily": return target_date >= self.due_at.date()
        if self.recurrence == "weekly": return target_date >= self.due_at.date() and target_date.weekday() == self.due_at.weekday()
        return self.due_at.date() == target_date
    def scheduled_for(self, target_date: date) -> "Task":
        """Return a dated occurrence with this task's time and details."""
        return Task(self.description, datetime.combine(target_date, self.due_at.time()), self.duration_minutes, self.priority, self.completed, self.recurrence)
    @property
    def ends_at(self) -> datetime:
        """Return the end of this task's scheduled block."""
        return self.due_at + timedelta(minutes=self.duration_minutes)
    def to_dict(self) -> dict:
        """Serialize this task for JSON."""
        return {"description": self.description, "due_at": self.due_at.isoformat(), "duration_minutes": self.duration_minutes, "priority": self.priority, "completed": self.completed, "recurrence": self.recurrence}
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create a task from JSON data."""
        return cls(data["description"], datetime.fromisoformat(data["due_at"]), data.get("duration_minutes", 30), data.get("priority", "medium"), data.get("completed", False), data.get("recurrence", "none"))

@dataclass
class Pet:
    """A pet and its assigned care tasks."""
    name: str
    species: str
    pet_id: str = ""
    tasks: list[Task] = field(default_factory=list)
    def add_task(self, task: Task) -> None:
        """Assign a task to this pet."""
        self.tasks.append(task)
    def list_tasks(self, include_completed: bool = True) -> list[Task]:
        """List tasks, optionally excluding completed work."""
        return [task for task in self.tasks if include_completed or not task.completed]
    def to_dict(self) -> dict:
        """Serialize this pet and its tasks."""
        return {"name": self.name, "species": self.species, "pet_id": self.pet_id, "tasks": [task.to_dict() for task in self.tasks]}
    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Create a pet from JSON data."""
        return cls(data["name"], data["species"], data.get("pet_id", ""), [Task.from_dict(task) for task in data.get("tasks", [])])

@dataclass
class Owner:
    """A pet owner who may manage several pets."""
    name: str
    pets: list[Pet] = field(default_factory=list)
    def add_pet(self, pet: Pet) -> None:
        """Add a uniquely named pet."""
        if self.get_pet(pet.name): raise ValueError(f"A pet named {pet.name} already exists.")
        self.pets.append(pet)
    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name without case sensitivity."""
        return next((pet for pet in self.pets if pet.name.casefold() == name.casefold()), None)
    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return each task with the pet it belongs to."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]
    def to_dict(self) -> dict:
        """Serialize the owner and pets."""
        return {"name": self.name, "pets": [pet.to_dict() for pet in self.pets]}
    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Create an owner from JSON data."""
        return cls(data["name"], [Pet.from_dict(pet) for pet in data.get("pets", [])])

class Scheduler:
    """Builds cross-pet schedules from one owner's tasks."""
    def __init__(self, owner: Owner) -> None:
        """Store the owner whose tasks are scheduled."""
        self.owner = owner
    def tasks_for_day(self, target_date: date | None = None, include_completed: bool = False) -> list[tuple[Pet, Task]]:
        """Return unfinished dated occurrences, sorted by starting time."""
        target_date = target_date or date.today()
        tasks = [(pet, task.scheduled_for(target_date)) for pet, task in self.owner.get_all_tasks() if task.occurs_on(target_date) and (include_completed or not task.completed)]
        return self.sort_by_due_time(tasks)
    def sort_by_due_time(self, tasks: list[tuple[Pet, Task]] | None = None) -> list[tuple[Pet, Task]]:
        """Sort task-pet pairs by scheduled start."""
        return sorted(tasks if tasks is not None else self.owner.get_all_tasks(), key=lambda item: item[1].due_at)
    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[tuple[Pet, Task]]:
        """Filter tasks by pet and/or completion status."""
        return [(pet, task) for pet, task in self.owner.get_all_tasks() if (pet_name is None or pet.name.casefold() == pet_name.casefold()) and (completed is None or task.completed == completed)]
    def find_conflicts(self, target_date: date | None = None) -> list[tuple[tuple[Pet, Task], tuple[Pet, Task]]]:
        """Return unfinished task pairs whose scheduled windows overlap."""
        schedule, conflicts = self.tasks_for_day(target_date), []
        for index, current in enumerate(schedule):
            for later in schedule[index + 1:]:
                if later[1].due_at < current[1].ends_at: conflicts.append((current, later))
                else: break
        return conflicts

def save_owner(owner: Owner, path: str | Path) -> None:
    """Save owner data as JSON."""
    Path(path).write_text(json.dumps(owner.to_dict(), indent=2), encoding="utf-8")
def load_owner(path: str | Path) -> Owner:
    """Load owner data from JSON."""
    return Owner.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
