"""Streamlit interface for PawPal+."""
from datetime import datetime
from pathlib import Path
import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task, load_owner, save_owner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Plan pet care across your household and catch overlapping tasks early.")
if "owner" not in st.session_state: st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
owner.name = st.text_input("Owner name", value=owner.name)
storage_path = Path("pawpal_data.json")
left, right = st.columns(2)
with left:
    if st.button("Save data"):
        save_owner(owner, storage_path); st.success("Saved pawpal_data.json.")
with right:
    if st.button("Load saved data"):
        if storage_path.exists(): st.session_state.owner = load_owner(storage_path); st.rerun()
        else: st.warning("No saved data yet.")

st.subheader("Pets")
with st.form("pet_form", clear_on_submit=True):
    name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and name.strip():
        try: owner.add_pet(Pet(name.strip(), species)); st.success(f"Added {name.strip()}.")
        except ValueError as error: st.error(str(error))

if not owner.pets:
    st.info("Add a pet to start planning.")
else:
    st.subheader("Add a task")
    with st.form("task_form", clear_on_submit=True):
        pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])
        description = st.text_input("Task description")
        due_date = st.date_input("Due date")
        due_time = st.time_input("Due time")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"])
        if st.form_submit_button("Add task") and description.strip():
            owner.get_pet(pet_name).add_task(Task(description.strip(), datetime.combine(due_date, due_time), int(duration), priority, recurrence=recurrence))
            st.success("Task added.")
    st.subheader("Today’s Schedule")
    scheduler = Scheduler(owner)
    schedule = scheduler.tasks_for_day()
    if schedule:
        st.table([{"Time": task.due_at.strftime("%H:%M"), "Pet": pet.name, "Task": task.description, "Minutes": task.duration_minutes, "Priority": task.priority} for pet, task in schedule])
    else: st.info("No unfinished tasks scheduled for today.")
    for first, second in scheduler.find_conflicts():
        st.warning(f"Conflict: {first[0].name}'s {first[1].description} overlaps {second[0].name}'s {second[1].description}.")
